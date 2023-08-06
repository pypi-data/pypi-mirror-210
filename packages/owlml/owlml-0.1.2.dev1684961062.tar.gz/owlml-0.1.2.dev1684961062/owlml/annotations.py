"""Annotations functions."""
import json
from pathlib import Path
from typing import Any, Union


def read_annotations(data_directory: Union[str, Path], version: str) -> dict[str, Any]:
    """Read annotations."""
    data_directory = Path(data_directory)
    annotations_paths = [
        p for p in data_directory.glob("**/annotations/*.json") if p.stem == version
    ]
    if len(annotations_paths) == 0:
        raise ValueError(f"No annotations for version {version}.")
    elif len(annotations_paths) > 1:
        raise ValueError(f"Multiple annotations for version {version}.")
    annotations_path = annotations_paths[0]
    with open(annotations_path, "r") as f:
        return json.loads(f.read())


def extract_labels(dataset: dict[str, Any]) -> list[str]:
    """Get labels from dataset."""
    label_objects = dataset.get("categories", {}).get("label", {}).get("labels", [])
    return [l["name"] for l in label_objects]
