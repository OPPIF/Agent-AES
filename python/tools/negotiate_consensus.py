"""
Agent Consensus Negotiation Tool
Facilitates negotiation and consensus building between agents
"""

import json
from python.helpers.tool import Tool, Response
from python.helpers.agent_orchestrator import get_orchestrator, AgentRole
from python.helpers.print_style import PrintStyle


class NegotiateConsensus(Tool):
    """
    Tool for facilitating negotiation and consensus building between agents
    """
    
    async def execute(self, **kwargs):
        topic = kwargs.get("topic", "")
        agents = kwargs.get("agents", [])
        threshold = float(kwargs.get("threshold", 0.7))
        
        if not topic:
            return Response(
                message="Error: Negotiation topic is required",
                break_loop=False
            )
        
        if not agents or len(agents) < 2:
            return Response(
                message="Error: At least 2 agents are required for negotiation",
                break_loop=False
            )
        
        try:
            # Get orchestrator instance
            orchestrator = get_orchestrator(self.agent)
            
            # Ensure we have enough agents for negotiation
            available_agents = list(orchestrator.agents.keys())
            
            if len(available_agents) < len(agents):
                # Create additional agents if needed
                roles_needed = [AgentRole.ANALYST, AgentRole.CREATIVE, AgentRole.VALIDATOR]
                for i, role in enumerate(roles_needed[:len(agents) - len(available_agents)]):
                    new_agent_id = await orchestrator.create_specialized_agent(
                        role=role,
                        task_description=f"Participate in negotiation about: {topic}"
                    )
                    available_agents.append(new_agent_id)
            
            # Use the first N available agents
            participating_agents = available_agents[:len(agents)]
            
            # Conduct negotiation
            negotiation_result = await orchestrator.negotiate_consensus(
                topic=topic,
                participating_agents=participating_agents,
                consensus_threshold=threshold
            )
            
            # Format response
            response_text = f"""
# 🤝 Agent Consensus Negotiation Results

## Topic
{topic}

## Negotiation Summary
- **Consensus Reached**: {'✅ Yes' if negotiation_result['consensus_reached'] else '❌ No'}
- **Rounds Conducted**: {len(negotiation_result['rounds'])}
- **Participating Agents**: {len(negotiation_result['participants'])}

## Final Decision
{negotiation_result['final_decision']['decision']}

## Decision Rationale
{negotiation_result['final_decision'].get('rationale', 'No rationale provided')}

## Negotiation Process
"""
            
            for i, round_data in enumerate(negotiation_result['rounds'], 1):
                response_text += f"""
### Round {i}
"""
                for agent_id, position in round_data['positions'].items():
                    if 'error' not in position:
                        agent_role = orchestrator.agents[agent_id].role.value
                        response_text += f"""
**{agent_role.title()} Agent Position:**
- Stance: {position.get('position', 'No position stated')}
- Key Arguments: {', '.join(position.get('arguments', []))}
- Willing to Compromise: {', '.join(position.get('compromises', []))}

"""
            
            if negotiation_result['final_decision'].get('implementation_steps'):
                response_text += f"""
## Implementation Steps
"""
                for step in negotiation_result['final_decision']['implementation_steps']:
                    response_text += f"- {step}\n"
            
            return Response(message=response_text, break_loop=False)
            
        except Exception as e:
            error_msg = f"Negotiation failed: {str(e)}"
            PrintStyle(font_color="red").print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def before_execution(self, **kwargs):
        PrintStyle(
            font_color="#1B4F72", 
            background_color="white", 
            bold=True, 
            padding=True
        ).print(f"{self.agent.agent_name}: Starting Agent Consensus Negotiation")
        
        self.log = self.agent.context.log.log(
            type="tool",
            heading="🤝 Agent Consensus Negotiation",
            content="Facilitating negotiation between specialized agents",
            kvps=self.args
        )