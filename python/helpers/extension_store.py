from __future__ import annotations

"""Extension store manager.

This module provides a minimal helper for discovering and installing
publicly available extensions or tools.  The store is represented by an
index JSON document that lists packages and includes a SHA256 digest for
each archive.  Only packages with a valid digest are returned.

The store does **not** attempt to be feature complete; it is a thin layer
used by the ``extension_install`` tool to fetch and install extensions at
runtime.
"""

import hashlib
import io
import json
import os
import urllib.request
import zipfile
from dataclasses import dataclass
from typing import Iterable, List, Optional

from . import files


@dataclass
class ExtensionPackage:
    """Metadata describing an extension or tool package."""

    name: str
    url: str
    sha256: str
    kind: str = "extension"  # either "extension" or "tool"
    extension_point: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None


class ExtensionStore:
    """Simple client for an extension index."""

    def __init__(self, index_url: str) -> None:
        self.index_url = index_url

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------
    def list_extensions(self) -> List[ExtensionPackage]:
        """Return all packages from the remote index.

        The index is expected to be a JSON document containing a list of
        entries with the keys described in :class:`ExtensionPackage`.
        Only entries that provide a ``sha256`` field are returned, making
        them "signed" in the sense that their integrity can be verified
        before installation.
        """

        with urllib.request.urlopen(self.index_url) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if isinstance(data, dict):
            entries: Iterable[dict] = data.get("extensions", [])
        else:
            entries = data

        packages: List[ExtensionPackage] = []
        for item in entries:
            if "sha256" not in item:
                continue
            packages.append(
                ExtensionPackage(
                    name=item["name"],
                    url=item["url"],
                    sha256=item["sha256"],
                    kind=item.get("kind", "extension"),
                    extension_point=item.get("extension_point"),
                    version=item.get("version"),
                    description=item.get("description"),
                )
            )
        return packages

    # ------------------------------------------------------------------
    # Download / verify / install
    # ------------------------------------------------------------------
    def download(self, package: ExtensionPackage) -> bytes:
        """Download the raw archive for ``package``."""
        with urllib.request.urlopen(package.url) as resp:
            return resp.read()

    def verify(self, package: ExtensionPackage, data: bytes) -> bool:
        """Verify the downloaded archive against the signed hash."""
        digest = hashlib.sha256(data).hexdigest()
        return digest.lower() == package.sha256.lower()

    def install(self, package: ExtensionPackage, data: bytes, base_dir: str | None = None) -> str:
        """Install ``package`` after it has been downloaded.

        The archive is expected to be a ZIP file.  The contents are
        extracted into the appropriate directory depending on ``package.kind``:

        * ``tool``      -> ``python/tools``
        * ``extension`` -> ``python/extensions/{extension_point}``

        The installation path is returned.
        """
        if not self.verify(package, data):
            raise ValueError("Package signature mismatch")

        if base_dir is None:
            base_dir = files.get_abs_path("")

        if package.kind == "tool":
            target_dir = files.get_abs_path("python", "tools")
        else:
            if not package.extension_point:
                raise ValueError("Extension package missing extension_point")
            target_dir = files.get_abs_path("python", "extensions", package.extension_point)
        os.makedirs(target_dir, exist_ok=True)

        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            self._safe_extract(zf, target_dir)

        if package.kind == "extension":
            # refresh extension cache so newly installed code is picked up
            try:
                from . import extension as extension_helper

                extension_helper.invalidate_cache()
            except Exception:
                pass

        return target_dir

    # ------------------------------------------------------------------
    def _safe_extract(self, zf: zipfile.ZipFile, dest: str) -> None:
        """Extract ``zf`` into ``dest`` ensuring no path traversal."""
        for member in zf.infolist():
            # build the normalized absolute path
            member_path = os.path.join(dest, member.filename)
            abs_path = os.path.abspath(member_path)
            if not abs_path.startswith(os.path.abspath(dest)):
                raise ValueError(f"Unsafe path detected in archive: {member.filename}")
        zf.extractall(dest)


__all__ = ["ExtensionStore", "ExtensionPackage"]
