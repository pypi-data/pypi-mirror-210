"""OwlML datasets API."""
import json
import time
import warnings
from pathlib import Path
from typing import Any, Callable, Optional, Union

import datumaro as dm
from farmhash import fingerprint64
from tqdm import tqdm

from .annotations import read_annotations
from .api import OwlMLAPI
from .images import _download_image, generate_image_id, list_local_images


def create_dataset(org: str, slug: str, labels: list[str]) -> dict[str, Any]:
    """Create a dataset."""
    payload = dict(org=org, slug=slug, labels=labels)
    return OwlMLAPI.post("datasets", payload)


def download_dataset(
    dataset: str,
    version: Optional[str] = None,
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
        _download_image(image["presigned_get"], image_path)


def generate_records(
    dataset_directory: Union[str, Path],
    version: str,
    holdout_evaluator: Optional[Callable[[int], bool]] = None,
) -> list[dict[str, Any]]:
    """Generate dataset records for training or evaluation."""
    dataset_directory = Path(dataset_directory)
    image_map = {generate_image_id(p): p for p in list_local_images(dataset_directory)}
    dataset = read_annotations(dataset_directory, version)
    categories = dataset.categories().get(dm.AnnotationType.label)
    if categories is None:
        raise ValueError("Dataset does not contain labels.")
    labels = [l.name for l in categories.items]
    records = []
    for item in dataset:
        if holdout_evaluator and not holdout_evaluator(fingerprint64(item.id)):
            continue
        image_path = image_map.get(item.id)
        if image_path is None:
            warnings.warn(f"Image {item.id} not found.")
            continue
        item_labels = []
        for annotation in item.annotations:
            item_labels.append(labels[annotation.label])
        records.append(dict(image_path=image_path, labels=item_labels))
    return records


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
