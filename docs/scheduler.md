# Scheduler

The scheduler executes background tasks defined by the agent. Before a task starts, the scheduler checks system resources using `python/helpers/resource_monitor.py`.

Default limits can be adjusted in the module:

```python
DEFAULT_LIMITS = {"cpu": 90.0, "ram": 90.0, "gpu": 90.0}
```

If CPU, RAM or GPU usage exceeds these percentages, the task is postponed and retried on the next tick.

Agents can request a snapshot of current usage via the `resource_report` tool.
