import asyncio
import sys
import types
import importlib

# Stub heavy modules before importing TaskScheduler
litellm_stub = types.ModuleType("litellm")
litellm_stub.completion = None
litellm_stub.acompletion = None
litellm_stub.embedding = None
sys.modules.setdefault("litellm", litellm_stub)

dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda *a, **k: None
sys.modules.setdefault("dotenv", dotenv_stub)

agent_stub = types.ModuleType("agent")
class _Dummy:
    pass
agent_stub.Agent = _Dummy
agent_stub.AgentContext = _Dummy
agent_stub.UserMessage = _Dummy
sys.modules.setdefault("agent", agent_stub)

initialize_stub = types.ModuleType("initialize")
initialize_stub.initialize_agent = lambda *a, **k: None
sys.modules.setdefault("initialize", initialize_stub)

persist_chat_stub = types.ModuleType("python.helpers.persist_chat")
persist_chat_stub.save_tmp_chat = lambda *a, **k: None
sys.modules.setdefault("python.helpers.persist_chat", persist_chat_stub)

print_style_stub = types.ModuleType("python.helpers.print_style")
class PrintStyle:
    def __init__(self, *a, **k): pass
    def print(self, *a, **k): pass
    def stream(self, *a, **k): pass
print_style_stub.PrintStyle = PrintStyle
sys.modules.setdefault("python.helpers.print_style", print_style_stub)

defer_stub = types.ModuleType("python.helpers.defer")
class DeferredTask:
    def __init__(self, thread_name="Background"): pass
    def start_task(self, func, *args, **kwargs):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(func(*args, **kwargs))
        loop.close()
        return self
    def kill(self, *a, **k): pass
    def add_child_task(self, *a, **k): pass

defer_stub.DeferredTask = DeferredTask
sys.modules.setdefault("python.helpers.defer", defer_stub)

files_stub = types.ModuleType("python.helpers.files")
files_stub.get_abs_path = lambda *a, **k: ""
files_stub.make_dirs = lambda *a, **k: None
files_stub.read_file = lambda *a, **k: ""
files_stub.write_file = lambda *a, **k: None
sys.modules.setdefault("python.helpers.files", files_stub)

localization_stub = types.ModuleType("python.helpers.localization")
class Localization:
    @staticmethod
    def get():
        class _Loc:
            def get_timezone(self):
                return "UTC"
        return _Loc()
localization_stub.Localization = Localization
sys.modules.setdefault("python.helpers.localization", localization_stub)

# Now import modules under test
TS = importlib.import_module("python.helpers.task_scheduler")
RM = importlib.import_module("python.helpers.resource_monitor")


def test_task_postponed_on_high_load(monkeypatch):
    monkeypatch.setattr(RM, "within_limits", lambda *a, **k: False)
    scheduler = TS.TaskScheduler.get()
    task = TS.AdHocTask.create(name="t", system_prompt="", prompt="", attachments=[], token="123")
    scheduler._tasks.tasks.append(task)

    run_called = False

    async def on_run(self):
        nonlocal run_called
        run_called = True

    monkeypatch.setattr(TS.AdHocTask, "on_run", on_run, raising=False)
    asyncio.run(scheduler._run_task(task))

    assert task.state == TS.TaskState.IDLE
    assert run_called is False
