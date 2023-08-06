"""OwlML experiments module."""
import os

from .api import OwlMLAPI


def generate_mlflow_url() -> str:
    """Get the MLflow URL."""
    return os.path.join(OwlMLAPI.base_url, "mlflow/")
