import asyncio
import json
import ssl
from dataclasses import dataclass
from typing import Any, Dict, Optional

import paramiko
from websockets.client import connect

from .docker import DockerContainerManager


@dataclass
class RemoteAgent:
    """Represents a remote agent accessible over a secure RPC channel."""

    uri: str
    ssl_cert: Optional[str] = None
    _ssl_context: Optional[ssl.SSLContext] = None

    def __post_init__(self) -> None:
        if self.ssl_cert:
            context = ssl.create_default_context(cafile=self.ssl_cert)
            context.check_hostname = False
            self._ssl_context = context
        else:
            self._ssl_context = None

    async def run_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a task payload to the remote agent and return the result."""
        async with connect(self.uri, ssl=self._ssl_context) as websocket:
            await websocket.send(json.dumps(payload))
            reply = await websocket.recv()
            return json.loads(reply)

    @classmethod
    def from_ssh(
        cls,
        host: str,
        username: str,
        key_filename: str,
        *,
        port: int = 22,
        rpc_port: int = 8765,
        ssl_cert: Optional[str] = None,
    ) -> "RemoteAgent":
        """Create a RemoteAgent by connecting to a machine over SSH.

        Assumes that an RPC server is already running on the remote machine.
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, port=port, username=username, key_filename=key_filename)
        client.close()
        scheme = "wss" if ssl_cert else "ws"
        uri = f"{scheme}://{host}:{rpc_port}"
        return cls(uri, ssl_cert=ssl_cert)

    @classmethod
    def from_docker(
        cls,
        image: str,
        name: str,
        *,
        rpc_port: int = 8765,
        ssl_cert: Optional[str] = None,
    ) -> "RemoteAgent":
        """Create a RemoteAgent by starting a Docker container via the Docker API."""
        manager = DockerContainerManager(image=image, name=name, ports={"8765/tcp": rpc_port})
        manager.start_container()
        scheme = "wss" if ssl_cert else "ws"
        uri = f"{scheme}://localhost:{rpc_port}"
        return cls(uri, ssl_cert=ssl_cert)
