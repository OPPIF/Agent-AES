# Multi-machine Deployment

The platform can distribute work across multiple nodes. Remote agents expose
an RPC endpoint using secure WebSockets (wss) and can be launched through SSH
or via the Docker API. The `RemoteAgent` helper wraps these connection methods
and is used by the `TaskScheduler` to delegate tasks.

## Registering a remote agent

```python
from python.helpers.remote_agent import RemoteAgent
from python.helpers.task_scheduler import TaskScheduler

scheduler = TaskScheduler.get()
agent = RemoteAgent.from_ssh("host.example.com", "ubuntu", "/path/key.pem", rpc_port=8765, ssl_cert="ca.pem")
scheduler.register_remote_agent("edge-node", agent)
```

Tasks can now specify `agent_location="edge-node"` to execute on that node.

## Docker based agents

```python
agent = RemoteAgent.from_docker("agent-image", "agent1", rpc_port=8765)
scheduler.register_remote_agent("container", agent)
```

## Networking

Communication occurs over WebSockets secured with TLS. Provide a certificate to
`RemoteAgent` to enable verification. The remote node should run an RPC server
that understands the task payloads and returns JSON results.

## Testing

Integration tests use a local secure WebSocket server with a self-signed
certificate to ensure the RPC channel works end-to-end.
