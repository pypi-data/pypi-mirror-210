"""OwlML datasets API."""
import json
import time
from pathlib import Path
from typing import Any, Optional, Union

import requests
from tqdm import tqdm

from .api import OwlMLAPI, raise_for_status


def _complete_batch(batch: str) -> dict[str, Any]:
    """Complete a batch."""
    return OwlMLAPI.post(f"batches/{batch}/complete")


def _create_batch(dataset: str, batch: Optional[str] = None) -> dict[str, Any]:
    """Create a batch."""
    payload = dict(dataset=dataset)
    if batch is not None:
        payload["slug"] = batch
    return OwlMLAPI.post("batches", payload)


def create_dataset(org: str, slug: str, labels: list[str]) -> dict[str, Any]:
    """Create a dataset."""
    payload = dict(org=org, slug=slug, labels=labels)
    return OwlMLAPI.post("datasets", payload)


def download_dataset(
    dataset: str,
    version_slug: Optional[str] = None,
    output_path: Union[str, Path] = "./",
) -> dict[str, Any]:
    """Download dataset version."""
    output_path = Path(output_path)
    if version_slug is None:
        version = version_dataset(dataset)
        version_slug = version["slug"]
    version = OwlMLAPI.get(f"dataset-versions/{version_slug}")
    if len(version["images"]) == 0:
        raise ValueError(f"No images in dataset version {version_slug}.")
    image = next(iter(version["images"]))
    image_path = output_path / Path(image["image_id"] + image["extension"])
    dataset_path = image_path.parent.parent.parent
    annotations_path = dataset_path / "annotations" / f"{version_slug}.json"
    annotations_path.parent.mkdir(parents=True, exist_ok=True)
    with open(annotations_path, "w") as f:
        f.write(json.dumps(version["annotations"]))
    for image in tqdm(version["images"]):
        image_path = output_path / Path(image["image_id"] + image["extension"])
        image_path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(image["presigned_get"])
        raise_for_status(response)
        with open(image_path, "wb") as f:
            f.write(response.content)


def version_dataset(dataset: str, slug: Optional[str] = None) -> dict[str, Any]:
    """Version a dataset."""
    payload = dict(dataset=dataset)
    if slug is not None:
        payload["slug"] = slug
    version = OwlMLAPI.post("dataset-versions", payload)
    while version == {}:
        time.sleep(0.25)
        version = OwlMLAPI.post("dataset-versions", payload)
    return version
