from python.helpers.tool import Tool, Response
from python.helpers.call_llm import call_llm
from python.helpers.memory import Memory


class PromptOptimizer(Tool):

    async def execute(self, prompt: str = "", **kwargs):
        system = "You improve prompts for better LLM responses. Suggest alternative prompt variations."
        model = self.agent.context.main_llm
        suggestions = await call_llm(system, model, prompt)
        db = await Memory.get(self.agent)
        await db.insert_text(suggestions, {"area": Memory.Area.MAIN.value, "tag": "prompt_optimization", "original": prompt})
        return Response(message=suggestions, break_loop=False)
