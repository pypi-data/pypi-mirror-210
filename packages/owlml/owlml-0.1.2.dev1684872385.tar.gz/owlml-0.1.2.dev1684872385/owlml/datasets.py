"""OwlML datasets API."""
from typing import Any

from .api import OwlMLAPI


def create_dataset(org: str, slug: str, labels: list[str]) -> dict[str, Any]:
    """Create a dataset."""
    payload = dict(org=org, slug=slug, labels=labels)
    return OwlMLAPI.post("datasets", payload)


def _create_batch(dataset: str) -> dict[str, Any]:
    """Create a batch."""
    payload = dict(dataset=dataset)
    return OwlMLAPI.post("batches", payload)


def _complete_batch(batch: str) -> dict[str, Any]:
    """Complete a batch."""
    return OwlMLAPI.post(f"batches/{batch}/complete")
