import json
from python.helpers.tool import Tool, Response
from python.helpers import resource_monitor


class ResourceReport(Tool):

    async def execute(self, **kwargs):  # type: ignore[override]
        data = resource_monitor.report()
        return Response(message=json.dumps(data, indent=4), break_loop=False)
