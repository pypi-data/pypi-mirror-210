"""OwlML images API."""
import hashlib
from pathlib import Path
from typing import Any, Optional, Union

import requests
from PIL import Image
from tqdm import tqdm

from .api import OwlMLAPI, raise_for_status
from .datasets import _complete_batch, _create_batch


def _create_image(
    dataset: str, batch: str, image_path: Union[str, Path]
) -> dict[str, Any]:
    image = Image.open(image_path)
    width, height = image.size
    with open(image_path, "rb") as f:
        checksum = hashlib.md5(f.read()).hexdigest()
    payload = dict(
        dataset=dataset,
        batch=batch,
        filename=image_path.name,
        checksum=checksum,
        width=width,
        height=height,
    )
    return OwlMLAPI.post("images", payload)


def _upload_image(presigned_post: dict[str, Any], image_path: Union[str, Path]) -> None:
    """Upload an image."""
    files = {"file": open(image_path, "rb")}
    response = requests.post(
        presigned_post["url"], data=presigned_post["fields"], files=files
    )
    raise_for_status(response)


def _complete_image(image_id: str) -> dict[str, Any]:
    """Complete an image."""
    return OwlMLAPI.post(f"images/{image_id}/complete", dict())


def upload_images(
    dataset: str, image_directory: Union[str, Path], batch_slug: Optional[str] = None
) -> dict[str, Any]:
    """Upload images to a dataset."""
    batch = _create_batch(dataset, batch_slug)
    images = list(Path(image_directory).glob("*"))
    for image_path in tqdm(images):
        image_response = _create_image(dataset, batch["slug"], image_path)
        _upload_image(image_response["presigned_post"], image_path)
        _complete_image(image_response["id"])
    return _complete_batch(batch["slug"])
