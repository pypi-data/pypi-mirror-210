import os
import cv2
import time
import torch
import asyncio

import numpy as np

from PIL import Image
from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import Tuple
from typing import Optional
from fastapi import Response
from pydantic import Field
from pydantic import BaseModel
from cftool.cv import to_rgb
from cftool.cv import to_uint8
from cftool.cv import np_to_bytes
from cftool.cv import restrict_wh
from cftool.cv import get_suitable_size
from cftool.misc import shallow_copy_dict
from cfclient.models.core import ImageModel
from cflearn.api.cv.diffusion import ControlNetHints
from cflearn.models.cv.diffusion.utils import CONTROL_HINT_KEY
from cflearn.models.cv.diffusion.utils import CONTROL_HINT_START_KEY

from .utils import api_pool
from .utils import to_canvas
from .utils import resize_image
from .utils import to_contrast_rgb
from .utils import APIs
from .common import BaseSDTag
from .common import get_sd_from
from .common import register_sd
from .common import register_sd_inpainting
from .common import handle_diffusion_model
from .common import handle_diffusion_inpainting_model
from .common import IAlgorithm
from .common import ControlNetModel
from .common import ReturnArraysModel
from .common import ControlStrengthModel


root = os.path.dirname(__file__)
new_control_depth_endpoint = "/control_new/depth"
new_control_canny_endpoint = "/control_new/canny"
new_control_pose_endpoint = "/control_new/pose"
new_control_mlsd_endpoint = "/control_new/mlsd"
control_depth_hint_endpoint = "/control/depth_hint"
control_canny_hint_endpoint = "/control/canny_hint"
control_pose_hint_endpoint = "/control/pose_hint"
control_mlsd_hint_endpoint = "/control/mlsd_hint"


images_type = Tuple[np.ndarray, np.ndarray]
apply_response = Tuple[List[np.ndarray], Dict[str, float]]


class ControlNetModelPlaceholder(ControlStrengthModel, ControlNetModel):
    pass


class ControlNetBundle(BaseModel):
    type: ControlNetHints
    data: ControlNetModelPlaceholder


TKey = Tuple[str, str, bool]


def get_bundle_key(bundle: ControlNetBundle) -> TKey:
    return bundle.type, bundle.data.hint_url, bundle.data.bypass_annotator


def get_hint_url_key(url: str) -> str:
    return f"{url}-hint"


async def apply_control(
    self: IAlgorithm,
    common: ControlNetModel,
    controls: List[ControlNetBundle],
    normalized_inpainting_mask: Optional[np.ndarray] = None,
    **kwargs: Any,
) -> apply_response:
    api_key = APIs.SD_INPAINTING if common.use_inpainting else APIs.SD
    api = get_sd_from(api_key, common, no_change=True)
    need_change_device = api_pool.need_change_device(api_key)
    api.enable_control()
    # download images
    urls = set()
    is_hint = {}
    is_global = {}
    if common.url is not None:
        urls.add(common.url)
        is_global[common.url] = True
    if common.mask_url is not None:
        urls.add(common.mask_url)
        is_global[common.mask_url] = True
    for bundle in controls:
        if not bundle.data.hint_url:
            raise ValueError("hint url should be provided in `controls`")
        urls.add(bundle.data.hint_url)
        is_hint[bundle.data.hint_url] = True
    sorted_urls = sorted(urls)
    futures = [self.download_image_with_retry(url) for url in sorted_urls]
    images: List[Image.Image] = await asyncio.gather(*futures)
    ## make sure that every image should have the same size
    original_w, original_h = images[0].size
    for im in images[1:]:
        w, h = im.size
        if w != original_w or h != original_h:
            msg = f"image size mismatch: {(original_w, original_h)} vs {(w, h)}"
            raise ValueError(msg)
    ## construct a lookup table
    image_array_d: Dict[str, np.ndarray] = {}
    for url, image in zip(sorted_urls, images):
        i_is_global = is_global.get(url, False)
        i_is_hint = is_hint.get(url, False)
        if i_is_global:
            image_array_d[url] = np.array(to_rgb(image))
        if i_is_hint:
            image_array_d[get_hint_url_key(url)] = np.array(to_contrast_rgb(image))
    # gather detect resolution
    detect_resolutions = []
    for bundle in controls:
        detect_resolutions.append(getattr(bundle.data, "detect_resolution", None))
    # calculate suitable size
    resize_to_original = lambda array: cv2.resize(
        array,
        (original_w, original_h),
        interpolation=cv2.INTER_CUBIC,
    )
    w, h = restrict_wh(original_w, original_h, common.max_wh)
    w = get_suitable_size(w, 64)
    h = get_suitable_size(h, 64)
    # activate corresponding ControlNet
    t0 = time.time()
    hint_types = sorted(set(bundle.type for bundle in controls))
    if len(hint_types) > api.num_pool:
        msg = f"maximum number of control is {api.num_pool}, but got {len(hint_types)}"
        raise ValueError(msg)
    base_md = api.sd_weights.get(BaseSDTag) if common.no_switch else None
    api.switch_control(*hint_types, base_md=base_md)
    t1 = time.time()
    # gather hints
    all_keys: List[TKey] = []
    ## Tensor for input, ndarray for results
    all_key_values: Dict[TKey, Tuple[torch.Tensor, np.ndarray]] = {}
    all_annotator_change_device_times = []
    for bundle, detect_resolution in zip(controls, detect_resolutions):
        i_type = bundle.type
        i_data = bundle.data
        i_hint_image = image_array_d[get_hint_url_key(i_data.hint_url)]
        i_bypass_annotator = i_data.bypass_annotator
        key = get_bundle_key(bundle)
        all_keys.append(key)
        i_value = all_key_values.get(key)
        if i_value is not None:
            continue
        if detect_resolution is not None and not i_bypass_annotator:
            i_hint_image = resize_image(i_hint_image, detect_resolution)
        device = api.device
        use_half = api.use_half
        ht = time.time()
        if need_change_device:
            device = "cuda:0"
            use_half = True
            api.annotators[i_type].to(device, use_half=True)
        all_annotator_change_device_times.append(time.time() - ht)
        if i_bypass_annotator:
            i_o_hint_arr = i_hint_image
        else:
            i_o_hint_arr = api.get_hint_of(i_type, i_hint_image, **i_data.dict())
        ht = time.time()
        if need_change_device:
            api.annotators[i_type].to("cpu", use_half=False)
            torch.cuda.empty_cache()
        all_annotator_change_device_times.append(time.time() - ht)
        i_hint_array = cv2.resize(i_o_hint_arr, (w, h), interpolation=cv2.INTER_LINEAR)
        i_hint = torch.from_numpy(i_hint_array)[None].permute(0, 3, 1, 2)
        if use_half:
            i_hint = i_hint.half()
        i_hint = i_hint.contiguous().to(device) / 255.0
        all_key_values[key] = i_hint, i_o_hint_arr
    change_annotator_device_time = sum(all_annotator_change_device_times)
    t2 = time.time()
    # gather scales
    num_scales = api.m.num_control_scales
    all_scales = []
    for bundle in controls:
        i_type = bundle.type
        i_data = bundle.data
        all_scales.append(
            [
                i_data.control_strength * (0.825 ** float(12 - i))
                for i in range(num_scales)
            ]
            if i_data.guess_mode
            else ([i_data.control_strength] * num_scales)
        )
    api.m.control_scales = all_scales
    if not common.prompt:
        raise ValueError("prompt should be provided in `common`")
    cond = [common.prompt] * common.num_samples
    kw = shallow_copy_dict(kwargs)
    kw.update(handle_diffusion_model(api, common))
    hint = [(b.type, all_key_values[k][0]) for b, k in zip(controls, all_keys)]
    kw[CONTROL_HINT_KEY] = hint
    kw[CONTROL_HINT_START_KEY] = [b.data.hint_start for b in controls]
    kw["max_wh"] = common.max_wh
    dt = time.time()
    if need_change_device:
        api.to("cuda:0", use_half=True, no_annotator=True)
    change_diffusion_device_time = time.time() - dt
    # inpainting workaround
    common = common.copy()
    is_sd_inpainting = common.use_inpainting
    common.use_raw_inpainting = not is_sd_inpainting
    if common.mask_url is not None or is_sd_inpainting:
        if common.url is None:
            raise ValueError("`url` should be provided to inpainting")
        if normalized_inpainting_mask is not None:
            inpainting_mask = Image.fromarray(to_uint8(normalized_inpainting_mask))
        else:
            if common.mask_url is None:
                raise ValueError(
                    "either `mask_url` or `normalized_input_mask` "
                    "should be provided to perform ControlNet inpainting"
                )
            inpainting_mask = Image.fromarray(image_array_d[common.mask_url])
            inpainting_mask = inpainting_mask.convert("L")
        image = Image.fromarray(image_array_d[common.url])
        kw.update(handle_diffusion_inpainting_model(common))
        outs = api.txt2img_inpainting(cond, image, inpainting_mask, **kw)
    elif common.url is None:
        kw["size"] = w, h
        outs = api.txt2img(cond, **kw)
    else:
        init_image = cv2.resize(
            image_array_d[common.url],
            (w, h),
            interpolation=cv2.INTER_LINEAR,
        )
        init_image = init_image[None].repeat(common.num_samples, axis=0)
        init_image = init_image.transpose([0, 3, 1, 2])
        init_image = init_image.astype(np.float32) / 255.0
        kw["cond"] = cond
        kw["fidelity"] = common.fidelity
        init_tensor = torch.from_numpy(init_image)
        if api.use_half:
            init_tensor = init_tensor.half()
        init_tensor = init_tensor.to(api.device)
        outs = api.img2img(init_tensor, **kw)
    dt = time.time()
    api_pool.cleanup(api_key)
    change_diffusion_device_time += time.time() - dt
    outs = 0.5 * (outs + 1.0)
    outs = to_uint8(outs).permute(0, 2, 3, 1).cpu().numpy()
    t3 = time.time()
    results = list(map(resize_to_original, [p[1] for p in all_key_values.values()]))
    for i in range(common.num_samples):
        results.append(resize_to_original(outs[i]))
    latencies = dict(
        switch=t1 - t0,
        get_hint=t2 - t1 - change_annotator_device_time,
        change_annotator_device=change_annotator_device_time,
        inference=t3 - t2 - change_diffusion_device_time,
        change_diffusion_device=change_diffusion_device_time,
        post_resize=time.time() - t3,
    )
    return results, latencies


async def run_single_control(
    self: IAlgorithm,
    data: ControlNetModel,
    hint_type: ControlNetHints,
    **kwargs: Any,
) -> Tuple[List[np.ndarray], Dict[str, float]]:
    self.log_endpoint(data)
    bundle = ControlNetBundle(type=hint_type, data=data)
    return await apply_control(self, data, [bundle], **kwargs)


def register_control(
    algorithm_model_class: Type[ControlNetModel],
    algorithm_endpoint: str,
    hint_type: ControlNetHints,
) -> None:
    class _(IAlgorithm):
        model_class = algorithm_model_class

        endpoint = algorithm_endpoint

        def initialize(self) -> None:
            register_sd()
            register_sd_inpainting()

        async def run(
            self, data: algorithm_model_class, *args: Any, **kwargs: Any
        ) -> Response:
            rs, latencies = await run_single_control(self, data, hint_type, **kwargs)
            t0 = time.time()
            content = None if data.return_arrays else np_to_bytes(to_canvas(rs))
            t1 = time.time()
            latencies["to_canvas"] = t1 - t0
            self.log_times(latencies)
            if data.return_arrays:
                return rs
            return Response(content=content, media_type="image/png")

    IAlgorithm.auto_register()(_)
    control_hint2endpoints[hint_type] = algorithm_endpoint
    control_hint2data_models[hint_type] = algorithm_model_class


def register_hint(
    hint_model_class: Type,
    hint_endpoint: str,
    hint_type: ControlNetHints,
) -> None:
    class _(IAlgorithm):
        model_class = hint_model_class
        model_class.__name__ = hint_model_class.__name__

        endpoint = hint_endpoint

        def initialize(self) -> None:
            register_sd()

        async def run(self, data: hint_model_class, *args: Any) -> Response:
            t0 = time.time()
            image = await self.download_image_with_retry(data.url)
            w, h = image.size
            t1 = time.time()
            m = api_pool.get(APIs.SD)
            t2 = time.time()
            image = to_contrast_rgb(image)
            hint_image = np.array(image)
            detect_resolution = getattr(data, "detect_resolution", None)
            if detect_resolution is not None:
                hint_image = resize_image(hint_image, detect_resolution)
            hint = m.get_hint_of(hint_type, hint_image, **data.dict())
            hint = cv2.resize(hint, (w, h), interpolation=cv2.INTER_LINEAR)
            t3 = time.time()
            api_pool.cleanup(APIs.SD)
            self.log_times(
                dict(
                    download=t1 - t0,
                    get_model=t2 - t1,
                    inference=t3 - t2,
                    cleanup=time.time() - t3,
                )
            )
            if data.return_arrays:
                return [hint]
            return Response(content=np_to_bytes(hint), media_type="image/png")

    IAlgorithm.auto_register()(_)
    control_hint2hint_endpoints[hint_type] = hint_endpoint
    control_hint2hint_data_models[hint_type] = hint_model_class


class DetectResolutionModel(BaseModel):
    detect_resolution: int = Field(
        384,
        ge=128,
        le=1024,
        description="Detect resolution.",
    )


class LargeDetectResolutionModel(BaseModel):
    detect_resolution: int = Field(
        512,
        ge=128,
        le=1024,
        description="Detect resolution.",
    )


# ControlNet (depth2image)


class _DepthModel(DetectResolutionModel):
    pass


class ControlDepthModel(_DepthModel, ControlStrengthModel, ControlNetModel):
    pass


class ControlDepthHintModel(_DepthModel, ReturnArraysModel, ImageModel):
    pass


# ControlNet (canny2image)


class _CannyModel(LargeDetectResolutionModel):
    low_threshold: int = Field(
        100,
        ge=1,
        le=255,
        description="Low threshold of canny algorithm.",
    )
    high_threshold: int = Field(
        200,
        ge=1,
        le=255,
        description="High threshold of canny algorithm.",
    )


class ControlCannyModel(_CannyModel, ControlStrengthModel, ControlNetModel):
    pass


class ControlCannyHintModel(_CannyModel, ReturnArraysModel, ImageModel):
    pass


# ControlNet (pose2image)


class _PoseModel(LargeDetectResolutionModel):
    pass


class ControlPoseModel(_PoseModel, ControlStrengthModel, ControlNetModel):
    pass


class ControlPoseHintModel(_PoseModel, ReturnArraysModel, ImageModel):
    pass


# ControlNet (canny2image)


class _MLSDModel(LargeDetectResolutionModel):
    value_threshold: float = Field(
        0.1,
        ge=0.01,
        le=2.0,
        description="Value threshold of mlsd model.",
    )
    distance_threshold: float = Field(
        0.1,
        ge=0.01,
        le=20.0,
        description="Distance threshold of mlsd model.",
    )


class ControlMLSDModel(_MLSDModel, ControlStrengthModel, ControlNetModel):
    pass


class ControlMLSDHintModel(_MLSDModel, ReturnArraysModel, ImageModel):
    pass


# register

control_hint2endpoints: Dict[ControlNetHints, str] = {}
control_hint2hint_endpoints: Dict[ControlNetHints, str] = {}
control_hint2data_models: Dict[ControlNetHints, Type[BaseModel]] = {}
control_hint2hint_data_models: Dict[ControlNetHints, Type[BaseModel]] = {}
register_control(ControlDepthModel, new_control_depth_endpoint, ControlNetHints.DEPTH)
register_control(ControlCannyModel, new_control_canny_endpoint, ControlNetHints.CANNY)
register_control(ControlPoseModel, new_control_pose_endpoint, ControlNetHints.POSE)
register_control(ControlMLSDModel, new_control_mlsd_endpoint, ControlNetHints.MLSD)
register_hint(ControlDepthHintModel, control_depth_hint_endpoint, ControlNetHints.DEPTH)
register_hint(ControlCannyHintModel, control_canny_hint_endpoint, ControlNetHints.CANNY)
register_hint(ControlPoseHintModel, control_pose_hint_endpoint, ControlNetHints.POSE)
register_hint(ControlMLSDHintModel, control_mlsd_hint_endpoint, ControlNetHints.MLSD)


__all__ = [
    "get_bundle_key",
    "new_control_depth_endpoint",
    "new_control_canny_endpoint",
    "new_control_pose_endpoint",
    "new_control_mlsd_endpoint",
    "control_depth_hint_endpoint",
    "control_canny_hint_endpoint",
    "control_pose_hint_endpoint",
    "control_mlsd_hint_endpoint",
    "ControlDepthModel",
    "ControlDepthHintModel",
    "ControlCannyModel",
    "ControlCannyHintModel",
    "ControlPoseModel",
    "ControlPoseHintModel",
    "ControlMLSDModel",
    "ControlMLSDHintModel",
    "control_hint2endpoints",
    "control_hint2hint_endpoints",
    "control_hint2data_models",
    "control_hint2hint_data_models",
]
