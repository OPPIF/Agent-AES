from python.helpers.extension import Extension
from python.helpers.self_reflection import SelfReflection
from agent import LoopData


class SelfReflectionExtension(Extension):

    async def execute(
        self,
        loop_data: LoopData = LoopData(),
        text: str = "",
        parsed: dict = {},
        **kwargs,
    ):
        if "tool_name" in parsed and parsed["tool_name"] == "response":
            await SelfReflection.analyze(self.agent)
