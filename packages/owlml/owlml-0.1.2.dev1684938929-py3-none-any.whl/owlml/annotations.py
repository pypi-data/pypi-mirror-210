"""Annotations functions."""
from pathlib import Path
from typing import Union

import datumaro as dm


def read_annotations(data_directory: Union[str, Path], version: str) -> dm.Dataset:
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
    return dm.Dataset.import_from(annotations_path, "datumaro")
