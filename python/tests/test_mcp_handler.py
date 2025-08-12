import os, sys, types, threading, time, pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Stub dependencies before importing the module under test
settings_stub = types.ModuleType("settings")
settings_stub.get_settings = lambda: {"mcp_client_init_timeout": 0, "mcp_client_tool_timeout": 0}
sys.modules["python.helpers.settings"] = settings_stub

print_style_stub = types.ModuleType("print_style")
class DummyPrintStyle:
    def __init__(self, *args, **kwargs):
        pass
    def print(self, *args, **kwargs):
        pass
    def stream(self, *args, **kwargs):
        pass
print_style_stub.PrintStyle = DummyPrintStyle
sys.modules["python.helpers.print_style"] = print_style_stub

tool_stub = types.ModuleType("tool")
class DummyTool:
    async def execute(self, **kwargs):
        pass
class DummyResponse:
    def __init__(self, message: str = "", break_loop: bool = False):
        self.message = message
        self.break_loop = break_loop
tool_stub.Tool = DummyTool
tool_stub.Response = DummyResponse
sys.modules["python.helpers.tool"] = tool_stub

from python.helpers.mcp_handler import MCPConfig

class DummyServer:
    def __init__(self, name: str):
        self.name = name
        self.description = "desc"
    def get_tools(self):
        return [{"name": "t", "description": "d", "input_schema": {}}]
    def get_log(self) -> str:
        return ""
    def get_error(self) -> str:
        return ""


def reset_config():
    MCPConfig._MCPConfig__lock = threading.Lock()
    MCPConfig._MCPConfig__init_condition = threading.Condition(MCPConfig._MCPConfig__lock)
    MCPConfig._MCPConfig__instance = MCPConfig(servers_list=[])
    MCPConfig._MCPConfig__initialized = False


def test_get_tools_prompt_no_servers():
    reset_config()
    config = MCPConfig.get_instance()
    with MCPConfig._MCPConfig__lock:
        MCPConfig._MCPConfig__initialized = True
        MCPConfig._MCPConfig__init_condition.notify_all()
    with pytest.raises(RuntimeError):
        config.get_tools_prompt()


def test_get_tools_prompt_waits_for_init():
    reset_config()
    config = MCPConfig.get_instance()
    config.servers = [DummyServer("s1")]

    def delayed_init():
        time.sleep(0.1)
        with MCPConfig._MCPConfig__lock:
            MCPConfig._MCPConfig__initialized = True
            MCPConfig._MCPConfig__init_condition.notify_all()

    t = threading.Thread(target=delayed_init)
    t.start()
    start = time.time()
    prompt = config.get_tools_prompt()
    elapsed = time.time() - start
    t.join()
    assert "s1" in prompt
    assert elapsed >= 0.1
