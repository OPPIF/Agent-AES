import asyncio
import json
import ssl
import subprocess
import tempfile

import websockets

import sys
from pathlib import Path

# Add repository root to path for direct imports
sys.path.append(str(Path(__file__).resolve().parents[2]))

from python.helpers.remote_agent import RemoteAgent


async def _start_echo_server(cert, key):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=cert, keyfile=key)

    async def handler(ws):
        msg = await ws.recv()
        await ws.send(msg)

    server = await websockets.serve(handler, "localhost", 0, ssl=ssl_context)
    return server


def _create_self_signed_cert():
    cert_fd, cert_path = tempfile.mkstemp()
    key_fd, key_path = tempfile.mkstemp()
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-nodes",
            "-days",
            "1",
            "-newkey",
            "rsa:2048",
            "-keyout",
            key_path,
            "-out",
            cert_path,
            "-subj",
            "/CN=localhost",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return cert_path, key_path


def test_remote_agent_rpc_roundtrip():
    cert, key = _create_self_signed_cert()

    async def run():
        server = await _start_echo_server(cert, key)
        port = server.sockets[0].getsockname()[1]
        agent = RemoteAgent(f"wss://localhost:{port}", ssl_cert=cert)
        result = await agent.run_task({"hello": "world"})
        assert result == {"hello": "world"}
        server.close()
        await server.wait_closed()

    asyncio.run(run())
