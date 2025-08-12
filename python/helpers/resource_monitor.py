import json
import psutil
import subprocess
from typing import Dict


def _gpu_usage() -> float:
    """Return GPU memory utilisation percentage using nvidia-smi.
    Returns 0.0 if GPU is not available or nvidia-smi is not installed."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total",
                "--format=csv,nounits,noheader",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        line = result.stdout.strip().split("\n")[0]
        used, total = [float(x.strip()) for x in line.split(",")]
        if total > 0:
            return used / total * 100.0
    except Exception:
        pass
    return 0.0


def usage() -> Dict[str, float]:
    """Return current resource usage percentages for CPU, RAM and GPU."""
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    gpu = _gpu_usage()
    return {"cpu": cpu, "ram": mem, "gpu": gpu}


DEFAULT_LIMITS: Dict[str, float] = {"cpu": 90.0, "ram": 90.0, "gpu": 90.0}


def within_limits(limits: Dict[str, float] | None = None) -> bool:
    """Check if current usage is below provided limits (in percent)."""
    limits = limits or DEFAULT_LIMITS
    current = usage()
    for key, limit in limits.items():
        if current.get(key, 0.0) > limit:
            return False
    return True


def report(limits: Dict[str, float] | None = None) -> Dict[str, float]:
    """Return a dict with current usage and limit information."""
    limits = limits or DEFAULT_LIMITS
    current = usage()
    current.update({f"{k}_limit": v for k, v in limits.items()})
    return current
