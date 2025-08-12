"""
Multi-Agent Orchestration Tool
Enables sophisticated coordination between specialized agents
"""

import json
from python.helpers.tool import Tool, Response
from python.helpers.agent_orchestrator import (
    get_orchestrator, AgentRole, CommunicationProtocol
)
from python.helpers.print_style import PrintStyle


class OrchestateAgents(Tool):
    """
    Tool for orchestrating multiple specialized agents to solve complex tasks
    """
    
    async def execute(self, **kwargs):
        task = kwargs.get("task", "")
        roles = kwargs.get("roles", [])
        strategy = kwargs.get("strategy", "collaborative")
        
        if not task:
            return Response(
                message="Error: Task description is required for orchestration",
                break_loop=False
            )
        
        if not roles:
            return Response(
                message="Error: At least one agent role must be specified",
                break_loop=False
            )
        
        try:
            # Convert string roles to AgentRole enums
            required_roles = []
            for role_str in roles:
                try:
                    role = AgentRole(role_str.lower())
                    required_roles.append(role)
                except ValueError:
                    return Response(
                        message=f"Error: Invalid agent role '{role_str}'. Valid roles: {[r.value for r in AgentRole]}",
                        break_loop=False
                    )
            
            # Get orchestrator instance
            orchestrator = get_orchestrator(self.agent)
            
            # Execute orchestrated task
            result = await orchestrator.orchestrate_task(
                task=task,
                required_roles=required_roles,
                coordination_strategy=strategy
            )
            
            # Format response
            response_text = f"""
# 🎭 Multi-Agent Orchestration Results

## Task
{task}

## Orchestration Summary
{result['summary']}

## Final Synthesis
{result['synthesis']}

## Performance Metrics
- **Total Duration**: {result['metrics']['total_duration']:.1f} seconds
- **Success Rate**: {result['metrics']['success_rate']:.1%}
- **Agents Involved**: {result['metrics']['agents_involved']}
- **Phases Completed**: {result['metrics']['phases_completed']}

## Agent Contributions
"""
            
            for contribution in result['contributions']:
                response_text += f"""
### {contribution['role'].title()} Agent ({contribution['phase']} phase)
{contribution['contribution']}

---
"""
            
            # Save orchestration results to memory
            db = await self.agent.context.log.log(
                type="info",
                heading="🎭 Orchestration Results Saved",
                content="Multi-agent orchestration results saved to memory"
            )
            
            return Response(message=response_text, break_loop=False)
            
        except Exception as e:
            error_msg = f"Orchestration failed: {str(e)}"
            PrintStyle(font_color="red").print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def before_execution(self, **kwargs):
        PrintStyle(
            font_color="#1B4F72", 
            background_color="white", 
            bold=True, 
            padding=True
        ).print(f"{self.agent.agent_name}: Starting Multi-Agent Orchestration")
        
        self.log = self.agent.context.log.log(
            type="tool",
            heading="🎭 Multi-Agent Orchestration",
            content="Initializing specialized agents for collaborative task execution",
            kvps=self.args
        )
        
        # Display orchestration parameters
        for key, value in self.args.items():
            PrintStyle(font_color="#85C1E9", bold=True).stream(
                self.nice_key(key) + ": "
            )
            PrintStyle(
                font_color="#85C1E9", 
                padding=isinstance(value, str) and "\n" in value
            ).stream(str(value))
            PrintStyle().print()