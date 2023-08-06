import os
from pathlib import Path
import urllib
import torch
from tqdm import tqdm
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
from typing import Union, Any, Dict, List

_MODELS = {
    "vit_b": " https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
    "vit_l": " https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
    "vit_h": " https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
}
_MODELS['default'] = _MODELS['vit_h']


def _download(url: str, root: str):
    os.makedirs(root, exist_ok=True)
    filename = os.path.basename(url)

    download_target = os.path.join(root, filename)

    if os.path.exists(download_target) and not os.path.isfile(download_target):
        raise RuntimeError(f"{download_target} exists and is not a regular file")

    if os.path.isfile(download_target):
        print('use model from', download_target)
        return download_target

    print('download model from', url)
    with urllib.request.urlopen(url) as source, open(download_target, "wb") as output:
        with tqdm(total=int(source.info().get("Content-Length")), ncols=80, unit='iB', unit_scale=True,
                  unit_divisor=1024) as loop:
            while True:
                buffer = source.read(8192)
                if not buffer:
                    break
                output.write(buffer)
                loop.update(len(buffer))
    return download_target

def available_models() -> List[str]:
    """Returns the names of available models"""
    return list(_MODELS.keys())

def get_amg_kwargs(args):
    amg_kwargs = {
        "points_per_side": args.get('points_per_side', None),
        "points_per_batch": args.get('points_per_batch', None),
        "pred_iou_thresh": args.get('pred_iou_thresh', None),
        "stability_score_thresh": args.get('stability_score_thresh', None),
        "stability_score_offset": args.get('stability_score_offset', None),
        "box_nms_thresh": args.get('box_nms_thresh', None),
        "crop_n_layers": args.get('crop_n_layers', None),
        "crop_nms_thresh": args.get('crop_nms_thresh', None),
        "crop_overlap_ratio": args.get('crop_overlap_ratio', None),
        "crop_n_points_downscale_factor": args.get('crop_n_points_downscale_factor', None),
        "min_mask_region_area": args.get('min_mask_region_area', None),
    }
    amg_kwargs = {k: v for k, v in amg_kwargs.items() if v is not None}
    return amg_kwargs

def load_model(model_type: str = 'default', device: Union[str, torch.device] = "cuda" if torch.cuda.is_available() else "cpu",
                   download_root: str = None):
    if model_type in _MODELS:
        checkpoint = _download(_MODELS[model_type], download_root or os.path.expanduser("~/.cache/SAM"))
    elif os.path.isfile(model_type):
        checkpoint = model_type
    else:
        raise RuntimeError(f"Model {model_type} not found; available models = {available_models()}")

    assert model_type in [
        "default",
        "vit_b",
        "vit_l",
        "vit_h",
    ], f"Unknown model_type {model_type}."
    print(f"Loading model {checkpoint}...")
    model = sam_model_registry[model_type](checkpoint=checkpoint)
    model.to(device=device)
    return model

def load_generator(sam = None, options: Dict[str, Any] = {}):
    sam = sam if sam is not None else load_model()
    print('sam', sam)
    output_mode = "coco_rle" if options.get('convert_to_rle', None) else "binary_mask"
    amg_kwargs = get_amg_kwargs(options)
    generator = SamAutomaticMaskGenerator(sam, output_mode=output_mode, **amg_kwargs)
    return generator


if __name__ == "__main__":
    load_model(download_root= Path.cwd())