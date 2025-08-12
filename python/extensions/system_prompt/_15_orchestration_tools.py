"""
Extension to include orchestration tools in system prompt
"""

from typing import Any
from python.helpers.extension import Extension
from agent import Agent, LoopData


class OrchestrationTools(Extension):

    async def execute(self, system_prompt: list[str] = [], loop_data: LoopData = LoopData(), **kwargs: Any):
        # Add orchestration tools to system prompt
        orchestration_prompt = get_orchestration_tools_prompt(self.agent)
        if orchestration_prompt:
            system_prompt.append(orchestration_prompt)


def get_orchestration_tools_prompt(agent: Agent) -> str:
    """Get orchestration tools prompt"""
    
    # Only add orchestration tools for main agent (A0) or coordinator agents
    if agent.number != 0 and agent.config.profile != "coordinator":
        return ""
    
    return agent.read_prompt("agent.system.orchestration_tools.md")