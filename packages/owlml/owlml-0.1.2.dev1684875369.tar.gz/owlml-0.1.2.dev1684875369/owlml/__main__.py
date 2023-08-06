"""Main entry point for OwlML CLI."""
import fire

from .auth import assign_batch, create_org, create_user, invite_user
from .datasets import create_dataset, download_dataset, version_dataset
from .images import upload_images


def main() -> None:
    """Expose CLI commands."""
    fire.Fire(
        {
            "assign-batch": assign_batch,
            "create-dataset": create_dataset,
            "create-org": create_org,
            "create-user": create_user,
            "download-dataset": download_dataset,
            "invite-user": invite_user,
            "upload-images": upload_images,
            "version-dataset": version_dataset,
        }
    )
