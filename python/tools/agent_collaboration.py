"""
Agent Collaboration Management Tool
Manages collaborative workflows between agents
"""

import json
from python.helpers.tool import Tool, Response
from python.helpers.agent_orchestrator import get_orchestrator, AgentRole
from python.helpers.print_style import PrintStyle


class AgentCollaboration(Tool):
    """
    Tool for managing collaborative workflows between agents
    """
    
    async def execute(self, **kwargs):
        action = kwargs.get("action", "status")
        
        if action == "status":
            return await self._get_orchestration_status()
        elif action == "create_team":
            return await self._create_agent_team(kwargs)
        elif action == "share_context":
            return await self._share_context(kwargs)
        elif action == "get_context":
            return await self._get_shared_context(kwargs)
        elif action == "list_agents":
            return await self._list_agents()
        else:
            return Response(
                message=f"Error: Unknown action '{action}'. Available actions: status, create_team, share_context, get_context, list_agents",
                break_loop=False
            )
    
    async def _get_orchestration_status(self) -> Response:
        """Get current orchestration status"""
        
        orchestrator = get_orchestrator(self.agent)
        status = orchestrator.get_orchestration_status()
        
        response_text = f"""
# 🎭 Agent Orchestration Status

## Overview
- **Total Agents**: {status['total_agents']}
- **Active Negotiations**: {status['active_negotiations']}
- **Shared Context Items**: {status['shared_context_items']}
- **Message Queue Size**: {status['message_queue_size']}

## Agents by Status
"""
        
        for status_name, count in status['agents_by_status'].items():
            if count > 0:
                response_text += f"- **{status_name.title()}**: {count}\n"
        
        response_text += "\n## Agents by Role\n"
        
        for role_name, count in status['agents_by_role'].items():
            if count > 0:
                response_text += f"- **{role_name.title()}**: {count}\n"
        
        # Add detailed agent information
        if orchestrator.agents:
            response_text += "\n## Detailed Agent Information\n"
            
            for agent_id, agent_node in orchestrator.agents.items():
                metrics = agent_node.performance_metrics
                response_text += f"""
### {agent_node.role.value.title()} Agent ({agent_id[:8]})
- **Status**: {agent_node.status.value}
- **Trust Score**: {agent_node.trust_score:.2f}
- **Tasks Completed**: {metrics.get('tasks_completed', 0)}
- **Success Rate**: {metrics.get('success_rate', 0):.1%}
- **Avg Duration**: {metrics.get('average_duration', 0):.1f}s
- **Capabilities**: {len(agent_node.capabilities)}

"""
        
        return Response(message=response_text, break_loop=False)
    
    async def _create_agent_team(self, kwargs) -> Response:
        """Create a team of specialized agents"""
        
        team_name = kwargs.get("team_name", "Unnamed Team")
        roles = kwargs.get("roles", [])
        purpose = kwargs.get("purpose", "General collaboration")
        
        if not roles:
            return Response(
                message="Error: Team roles must be specified",
                break_loop=False
            )
        
        try:
            orchestrator = get_orchestrator(self.agent)
            created_agents = []
            
            for role_str in roles:
                try:
                    role = AgentRole(role_str.lower())
                    agent_id = await orchestrator.create_specialized_agent(
                        role=role,
                        task_description=f"Member of {team_name} team for: {purpose}"
                    )
                    created_agents.append({
                        "id": agent_id,
                        "role": role.value
                    })
                except ValueError:
                    return Response(
                        message=f"Error: Invalid role '{role_str}'. Valid roles: {[r.value for r in AgentRole]}",
                        break_loop=False
                    )
            
            # Share team context
            await orchestrator.share_context(
                f"team_{team_name.lower().replace(' ', '_')}",
                {
                    "team_name": team_name,
                    "purpose": purpose,
                    "members": created_agents,
                    "created_at": datetime.now().isoformat()
                }
            )
            
            response_text = f"""
# 👥 Agent Team Created: {team_name}

## Purpose
{purpose}

## Team Members
"""
            
            for agent_info in created_agents:
                response_text += f"- **{agent_info['role'].title()}** Agent (ID: {agent_info['id'][:8]})\n"
            
            response_text += f"""
## Next Steps
- Use `orchestrate_agents` tool to assign collaborative tasks
- Use `agent_collaboration` with action 'share_context' to share information
- Monitor team performance with action 'status'
"""
            
            return Response(message=response_text, break_loop=False)
            
        except Exception as e:
            return Response(
                message=f"Error creating team: {str(e)}",
                break_loop=False
            )
    
    async def _share_context(self, kwargs) -> Response:
        """Share context between agents"""
        
        context_key = kwargs.get("context_key", "")
        context_data = kwargs.get("context_data", "")
        target_agents = kwargs.get("target_agents", None)
        
        if not context_key:
            return Response(
                message="Error: context_key is required",
                break_loop=False
            )
        
        try:
            orchestrator = get_orchestrator(self.agent)
            
            # Parse context_data if it's a JSON string
            if isinstance(context_data, str):
                try:
                    context_data = json.loads(context_data)
                except:
                    # Keep as string if not valid JSON
                    pass
            
            await orchestrator.share_context(
                context_key=context_key,
                context_data=context_data,
                target_agents=target_agents
            )
            
            response_text = f"""
# 📤 Context Shared Successfully

## Context Key
{context_key}

## Data Shared
{json.dumps(context_data, indent=2) if not isinstance(context_data, str) else context_data}

## Target Agents
{target_agents if target_agents else 'All agents'}
"""
            
            return Response(message=response_text, break_loop=False)
            
        except Exception as e:
            return Response(
                message=f"Error sharing context: {str(e)}",
                break_loop=False
            )
    
    async def _get_shared_context(self, kwargs) -> Response:
        """Retrieve shared context"""
        
        context_key = kwargs.get("context_key", "")
        
        if not context_key:
            return Response(
                message="Error: context_key is required",
                break_loop=False
            )
        
        try:
            orchestrator = get_orchestrator(self.agent)
            
            context_data = await orchestrator.get_shared_context(
                context_key=context_key,
                requesting_agent=self.agent.agent_name
            )
            
            if context_data is None:
                return Response(
                    message=f"No shared context found for key: {context_key}",
                    break_loop=False
                )
            
            response_text = f"""
# 📥 Shared Context Retrieved

## Context Key
{context_key}

## Context Data
{json.dumps(context_data, indent=2) if not isinstance(context_data, str) else context_data}
"""
            
            return Response(message=response_text, break_loop=False)
            
        except Exception as e:
            return Response(
                message=f"Error retrieving context: {str(e)}",
                break_loop=False
            )
    
    async def _list_agents(self) -> Response:
        """List all registered agents"""
        
        orchestrator = get_orchestrator(self.agent)
        
        if not orchestrator.agents:
            return Response(
                message="No agents currently registered in the orchestration system",
                break_loop=False
            )
        
        response_text = "# 🤖 Registered Agents\n\n"
        
        for agent_id, agent_node in orchestrator.agents.items():
            metrics = agent_node.performance_metrics
            response_text += f"""
## {agent_node.role.value.title()} Agent
- **ID**: {agent_id}
- **Status**: {agent_node.status.value}
- **Trust Score**: {agent_node.trust_score:.2f}
- **Current Task**: {agent_node.current_task or 'None'}

### Performance Metrics
- **Tasks Completed**: {metrics.get('tasks_completed', 0)}
- **Success Rate**: {metrics.get('success_rate', 0):.1%}
- **Average Duration**: {metrics.get('average_duration', 0):.1f}s
- **Quality Score**: {metrics.get('quality_score', 0):.2f}

### Capabilities
"""
            
            for capability in agent_node.capabilities:
                response_text += f"- **{capability.name}**: {capability.description} (Level {capability.complexity_level})\n"
            
            response_text += "\n---\n"
        
        return Response(message=response_text, break_loop=False)