"""OwlML images API."""
import hashlib
import os
from pathlib import Path
from typing import Any, Optional, Union

import requests
from PIL import Image
from tqdm import tqdm

from .api import OwlMLAPI, raise_for_status


def _complete_batch(batch: str) -> dict[str, Any]:
    """Complete a batch."""
    return OwlMLAPI.post(f"batches/{batch}/complete")


def _complete_image(image_id: str) -> dict[str, Any]:
    """Complete an image."""
    return OwlMLAPI.post(f"images/{image_id}/complete")


def _create_batch(dataset: str, batch: Optional[str] = None) -> dict[str, Any]:
    """Create a batch."""
    payload = dict(dataset=dataset)
    if batch is not None:
        payload["slug"] = batch
    return OwlMLAPI.post("batches", payload)


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


def _download_image(presigned_get: str, image_path: Union[str, Path]) -> None:
    """Download an image."""
    response = requests.get(presigned_get)
    raise_for_status(response)
    with open(image_path, "wb") as f:
        f.write(response.content)


def _upload_image(presigned_post: dict[str, Any], image_path: Union[str, Path]) -> None:
    """Upload an image."""
    files = {"file": open(image_path, "rb")}
    response = requests.post(
        presigned_post["url"], data=presigned_post["fields"], files=files
    )
    raise_for_status(response)


def generate_image_id(image_path: Union[str, Path]) -> str:
    """Generate an image ID."""
    org, dataset, batch, _, filename = str(image_path).split("/")[-5:]
    slug = Path(filename).stem
    return os.path.join(org, dataset, batch, "images", slug)


def list_local_images(data_directory: Union[str, Path]) -> list[Path]:
    """List local images."""
    return sorted(Path(data_directory).glob("**/images/*"))


def upload_images(
    dataset: str, image_directory: Union[str, Path], batch: Optional[str] = None
) -> dict[str, Any]:
    """Upload images to a dataset."""
    batch_response = _create_batch(dataset, batch)
    images = list(Path(image_directory).glob("*"))
    for image_path in tqdm(images):
        image_response = _create_image(dataset, batch_response["slug"], image_path)
        _upload_image(image_response["presigned_post"], image_path)
        _complete_image(image_response["id"])
    return _complete_batch(batch_response["slug"])
