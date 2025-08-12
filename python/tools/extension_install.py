from __future__ import annotations

"""Tool for installing extensions from the public store."""

from typing import Optional

from python.helpers.extension_store import ExtensionPackage, ExtensionStore
from python.helpers.tool import Response, Tool


DEFAULT_INDEX_URL = "https://example.com/extensions.json"


class ExtensionInstallTool(Tool):
    """Download, verify and install an extension or tool package.

    Expected arguments (at least one identifier must be provided):

    - ``name`` – name of the package listed in the index
    - ``url`` – direct URL to a package archive
    - ``sha256`` – expected digest when ``url`` is used directly
    - ``kind`` – ``"extension"`` or ``"tool"`` (default "extension")
    - ``extension_point`` – required when installing an extension
    - ``index_url`` – optional custom index URL
    """

    async def execute(self, **kwargs) -> Response:  # type: ignore[override]
        index_url = self.args.get("index_url", DEFAULT_INDEX_URL)
        store = ExtensionStore(index_url)

        pkg: Optional[ExtensionPackage] = None
        name = self.args.get("name")
        url = self.args.get("url")

        if name:
            for item in store.list_extensions():
                if item.name == name:
                    pkg = item
                    break
            if not pkg:
                return Response(message=f"Package '{name}' not found", break_loop=False)
        elif url:
            sha256 = self.args.get("sha256")
            if not sha256:
                return Response(message="sha256 is required when specifying a url", break_loop=False)
            pkg = ExtensionPackage(
                name=self.args.get("name", url.split("/")[-1]),
                url=url,
                sha256=sha256,
                kind=self.args.get("kind", "extension"),
                extension_point=self.args.get("extension_point"),
            )
        else:
            return Response(message="No package specified", break_loop=False)

        try:
            data = store.download(pkg)
            if not store.verify(pkg, data):
                return Response(message="Package signature mismatch", break_loop=False)
            store.install(pkg, data)
        except Exception as exc:  # pragma: no cover - defensive
            return Response(message=f"Installation failed: {exc}", break_loop=False)

        return Response(message=f"Installed package '{pkg.name}'", break_loop=False)


__all__ = ["ExtensionInstallTool"]
