import sys
import types
import asyncio
import importlib


class StubAgent:
    def read_prompt(self, *args, **kwargs):  # pragma: no cover - simple stub
        return "<TRUNCATED>"


def make_topic(contents):
    settings_stub = types.ModuleType("settings")
    settings_stub.get_settings = lambda: {
        "chat_model_ctx_length": 100,
        "chat_model_ctx_history": 1,
    }
    tokens_stub = types.ModuleType("tokens")
    tokens_stub.approximate_tokens = lambda text: len(text)

    orig_settings = sys.modules.get("python.helpers.settings")
    orig_tokens = sys.modules.get("python.helpers.tokens")
    sys.modules["python.helpers.settings"] = settings_stub
    sys.modules["python.helpers.tokens"] = tokens_stub

    history = importlib.reload(importlib.import_module("python.helpers.history"))

    if orig_settings is not None:
        sys.modules["python.helpers.settings"] = orig_settings
    else:
        del sys.modules["python.helpers.settings"]
    if orig_tokens is not None:
        sys.modules["python.helpers.tokens"] = orig_tokens
    else:
        del sys.modules["python.helpers.tokens"]

    topic = history.Topic(history=types.SimpleNamespace(agent=StubAgent()))
    for ai, content in contents:
        topic.add_message(ai, content)
    return topic


def test_compress_large_messages_selects_largest():
    topic = make_topic([(False, "a" * 30), (False, "b" * 50)])

    asyncio.run(topic.compress_large_messages())
    assert topic.messages[1].summary != ""
    assert topic.messages[0].summary == ""

    asyncio.run(topic.compress_large_messages())
    assert topic.messages[0].summary != ""


def test_compress_large_messages_mixed_set():
    topic = make_topic([(False, "short"), (False, "c" * 50)])

    assert asyncio.run(topic.compress_large_messages()) is True
    assert topic.messages[1].summary != ""
    assert topic.messages[0].summary == ""

    assert asyncio.run(topic.compress_large_messages()) is False
