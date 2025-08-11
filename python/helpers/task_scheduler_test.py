from datetime import datetime, timezone
import sys
import types

# Stub out optional heavy dependencies to keep import light
litellm_stub = types.ModuleType("litellm")
litellm_stub.completion = None
litellm_stub.acompletion = None
litellm_stub.embedding = None
sys.modules.setdefault("litellm", litellm_stub)

dotenv_stub = types.ModuleType("dotenv")
def _load_dotenv(*args, **kwargs):
    pass
dotenv_stub.load_dotenv = _load_dotenv
sys.modules.setdefault("dotenv", dotenv_stub)

# Create stubs for modules imported by task_scheduler but not needed for this test
agent_stub = types.ModuleType("agent")
class _Dummy:  # simple placeholder class
    pass
agent_stub.Agent = _Dummy
agent_stub.AgentContext = _Dummy
agent_stub.UserMessage = _Dummy
sys.modules.setdefault("agent", agent_stub)

initialize_stub = types.ModuleType("initialize")
def _initialize_agent(*args, **kwargs):
    pass
initialize_stub.initialize_agent = _initialize_agent
sys.modules.setdefault("initialize", initialize_stub)

persist_chat_stub = types.ModuleType("persist_chat")
def save_tmp_chat(*args, **kwargs):
    pass
persist_chat_stub.save_tmp_chat = save_tmp_chat
sys.modules.setdefault("python.helpers.persist_chat", persist_chat_stub)

print_style_stub = types.ModuleType("print_style")
class PrintStyle:
    pass
print_style_stub.PrintStyle = PrintStyle
sys.modules.setdefault("python.helpers.print_style", print_style_stub)

defer_stub = types.ModuleType("defer")
class DeferredTask:
    pass
defer_stub.DeferredTask = DeferredTask
sys.modules.setdefault("python.helpers.defer", defer_stub)

files_stub = types.ModuleType("files")
def get_abs_path(*args, **kwargs):
    return ""
def make_dirs(*args, **kwargs):
    pass
def read_file(*args, **kwargs):
    return ""
def write_file(*args, **kwargs):
    pass
files_stub.get_abs_path = get_abs_path
files_stub.make_dirs = make_dirs
files_stub.read_file = read_file
files_stub.write_file = write_file
sys.modules.setdefault("python.helpers.files", files_stub)

localization_stub = types.ModuleType("localization")
class Localization:
    @staticmethod
    def get():
        class _Loc:
            def get_timezone(self):
                return "UTC"
        return _Loc()
localization_stub.Localization = Localization
sys.modules.setdefault("python.helpers.localization", localization_stub)

from python.helpers.task_scheduler import TaskPlan


def test_create_returns_distinct_lists():
    plan1 = TaskPlan.create()
    plan2 = TaskPlan.create()

    assert plan1.todo is not plan2.todo
    assert plan1.done is not plan2.done

    plan1.todo.append(datetime.now(timezone.utc))
    assert plan2.todo == []
