import asyncio
import types
import sys
import pathlib
import pytest

# Ensure repository root is on sys.path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from python.helpers import settings, whisper


def test_background_tasks_run_once(monkeypatch):
    async def run_test():
        # Prepare initial settings without applying to avoid triggering tasks
        initial = settings.get_default_settings()
        settings.set_settings(initial, apply=False)

        # Stub agent and initialize modules before _apply_settings imports them
        stub_agent = types.SimpleNamespace(
            AgentContext=types.SimpleNamespace(_contexts={}, log_to_all=lambda **_: None)
        )
        monkeypatch.setitem(sys.modules, "agent", stub_agent)
        monkeypatch.setitem(
            sys.modules,
            "initialize",
            types.SimpleNamespace(
                initialize_agent=lambda: types.SimpleNamespace(mcp_servers="{}")
            ),
        )

        # Counters for background tasks
        preload_calls = 0
        mcp_update_calls = 0
        token_refresh_calls = 0

        async def fake_preload(model):
            nonlocal preload_calls
            preload_calls += 1

        def fake_mcp_update(servers):
            nonlocal mcp_update_calls
            mcp_update_calls += 1

        class StubMCPConfig:
            @classmethod
            def get_instance(cls):
                return cls()

            @classmethod
            def update(cls, servers):
                fake_mcp_update(servers)

            def model_dump_json(self):
                return "{}"

        class StubProxy:
            @classmethod
            def get_instance(cls):
                return cls()

            def reconfigure(self, token: str):
                nonlocal token_refresh_calls
                token_refresh_calls += 1

        monkeypatch.setitem(
            sys.modules,
            "python.helpers.mcp_handler",
            types.SimpleNamespace(MCPConfig=StubMCPConfig),
        )
        monkeypatch.setitem(
            sys.modules,
            "python.helpers.mcp_server",
            types.SimpleNamespace(DynamicMcpProxy=StubProxy),
        )

        monkeypatch.setattr(whisper, "preload", fake_preload)
        # Ensure token refresh triggers by changing returned token
        monkeypatch.setattr(settings, "create_auth_token", lambda: "token2")

        new_settings = dict(initial)
        new_settings["stt_model_size"] = "small"
        new_settings["mcp_servers"] = '{"mcpServers": {"x": {}}}'

        settings.set_settings(new_settings, apply=True)
        # Allow scheduled tasks to run
        await asyncio.sleep(0)

        assert preload_calls == 1
        assert mcp_update_calls == 1
        assert token_refresh_calls == 1

    asyncio.run(run_test())
