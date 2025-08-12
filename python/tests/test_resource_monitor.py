import types
import python.helpers.resource_monitor as rm


def _mock_psutil(monkeypatch, cpu, mem):
    monkeypatch.setattr(rm.psutil, "cpu_percent", lambda interval=None: cpu)
    memobj = types.SimpleNamespace(percent=mem)
    monkeypatch.setattr(rm.psutil, "virtual_memory", lambda: memobj)


def _mock_gpu(monkeypatch, used, total):
    class Result:
        stdout = f"{used},{total}\n"
    monkeypatch.setattr(rm.subprocess, "run", lambda *a, **k: Result())


def test_within_limits_low_load(monkeypatch):
    _mock_psutil(monkeypatch, 10, 20)
    _mock_gpu(monkeypatch, 1, 100)
    assert rm.within_limits({"cpu": 50, "ram": 50, "gpu": 50})


def test_within_limits_high_load(monkeypatch):
    _mock_psutil(monkeypatch, 95, 96)
    _mock_gpu(monkeypatch, 95, 100)
    assert not rm.within_limits({"cpu": 50, "ram": 50, "gpu": 50})

