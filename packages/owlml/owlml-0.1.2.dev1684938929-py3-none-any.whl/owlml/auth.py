"""Authentication functions for OwlML."""
from getpass import getpass
from typing import Any, Optional

from .api import OwlMLAPI


def assign_batch(batch: str, username: str) -> dict[str, Any]:
    """Assign a batch to a user."""
    payload = dict(username=username)
    return OwlMLAPI.post(f"batches/{batch}/assign", payload)


def create_user(username: str, email: Optional[str] = None) -> dict[str, Any]:
    """Create a user with the given username and password."""
    password = getpass("Password: ")
    assert password == getpass("Confirm password: ")
    payload = dict(username=username, password=password)
    if email is not None:
        payload["email"] = email
    return OwlMLAPI.post("users", payload)


def create_org(slug: str) -> dict[str, Any]:
    """Create an organization with the given slug."""
    return OwlMLAPI.post("orgs", dict(slug=slug))


def invite_user(org: str, username: str, role: str = "worker") -> dict[str, Any]:
    """Invite a user to an organization."""
    payload = dict(org=org, username=username, role=role)
    return OwlMLAPI.post(f"memberships", payload)
