"""OwlML datasets API."""
import time
from typing import Any, Optional

from .api import OwlMLAPI


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


def version_dataset(dataset: str, slug: Optional[str] = None) -> dict[str, Any]:
    """Version a dataset."""
    payload = dict(dataset=dataset)
    if slug is not None:
        payload["slug"] = slug
    response = OwlMLAPI.post("dataset-versions", payload)
    while response == {}:
        time.sleep(0.25)
        response = OwlMLAPI.post("dataset-versions", payload)
    return response
