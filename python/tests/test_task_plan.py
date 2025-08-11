from datetime import datetime, timedelta, tzinfo
import sys
from pathlib import Path
import types

# Add repository root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

# Provide minimal stubs for missing dependencies
nest_asyncio = types.ModuleType("nest_asyncio")
nest_asyncio.apply = lambda: None
sys.modules["nest_asyncio"] = nest_asyncio

crontab = types.ModuleType("crontab")
class CronTab:  # type: ignore
    pass
crontab.CronTab = CronTab
sys.modules["crontab"] = crontab

pydantic = types.ModuleType("pydantic")
class BaseModel:
    def __init__(self, **data):
        for k, v in data.items():
            setattr(self, k, v)

def Field(default=None, default_factory=None, **kwargs):
    if default_factory is not None:
        return default_factory()
    return default

class PrivateAttr:
    def __init__(self, default=None):
        self.default = default

pydantic.BaseModel = BaseModel
pydantic.Field = Field
pydantic.PrivateAttr = PrivateAttr
sys.modules["pydantic"] = pydantic

agent = types.ModuleType("agent")
class Agent: ...
class AgentContext: ...
class UserMessage: ...
agent.Agent = Agent
agent.AgentContext = AgentContext
agent.UserMessage = UserMessage
sys.modules["agent"] = agent

initialize = types.ModuleType("initialize")
def initialize_agent(*args, **kwargs):
    return None
initialize.initialize_agent = initialize_agent
sys.modules["initialize"] = initialize

persist_chat = types.ModuleType("python.helpers.persist_chat")
def save_tmp_chat(*args, **kwargs):
    return None
persist_chat.save_tmp_chat = save_tmp_chat
sys.modules["python.helpers.persist_chat"] = persist_chat

print_style = types.ModuleType("python.helpers.print_style")
class PrintStyle: ...
print_style.PrintStyle = PrintStyle
sys.modules["python.helpers.print_style"] = print_style

defer = types.ModuleType("python.helpers.defer")
class DeferredTask: ...
defer.DeferredTask = DeferredTask
sys.modules["python.helpers.defer"] = defer

files = types.ModuleType("python.helpers.files")
def get_abs_path(path):
    return path

def make_dirs(*args, **kwargs):
    return None

def read_file(*args, **kwargs):
    return ""

def write_file(*args, **kwargs):
    return None
files.get_abs_path = get_abs_path
files.make_dirs = make_dirs
files.read_file = read_file
files.write_file = write_file
sys.modules["python.helpers.files"] = files

localization = types.ModuleType("python.helpers.localization")
class Localization:
    @staticmethod
    def get():
        class _Loc:
            def get_timezone(self):
                return "UTC"
        return _Loc()
localization.Localization = Localization
sys.modules["python.helpers.localization"] = localization

pytz = types.ModuleType("pytz")
class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return timedelta(0)
    def localize(self, dt):
        return dt.replace(tzinfo=self)
UTC = UTC()

def timezone(name):
    if name == "UTC":
        return UTC
    raise ValueError("Only UTC supported")

pytz.timezone = timezone
pytz.UTC = UTC
sys.modules["pytz"] = pytz

from python.helpers.task_scheduler import TaskPlan


def is_utc(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) == timedelta(0)


def test_create_localizes_and_isolates_lists():
    naive_todo = datetime(2024, 1, 1, 12, 0, 0)
    naive_in_progress = datetime(2024, 1, 2, 12, 0, 0)
    naive_done = datetime(2024, 1, 3, 12, 0, 0)

    plan = TaskPlan.create(todo=[naive_todo], in_progress=naive_in_progress, done=[naive_done])

    assert is_utc(plan.todo[0])
    assert is_utc(plan.in_progress)
    assert is_utc(plan.done[0])

    plan_default = TaskPlan.create()

    assert plan_default.todo is not plan.todo
    assert plan_default.done is not plan.done
