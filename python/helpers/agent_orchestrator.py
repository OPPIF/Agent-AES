"""
Advanced Multi-Agent Orchestration System
Provides sophisticated coordination between specialized agents
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from agent import Agent, AgentContext, UserMessage
from python.helpers.print_style import PrintStyle
from python.helpers import memory, files
from python.helpers.log import LogItem


class AgentRole(Enum):
    """Specialized agent roles for different tasks"""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    SECURITY = "security"
    CREATIVE = "creative"
    VALIDATOR = "validator"


class CommunicationProtocol(Enum):
    """Communication protocols between agents"""
    DIRECT = "direct"
    BROADCAST = "broadcast"
    CONSENSUS = "consensus"
    NEGOTIATION = "negotiation"
    DELEGATION = "delegation"


class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentCapability:
    """Defines what an agent can do"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    complexity_level: int  # 1-10
    estimated_time: int  # seconds
    dependencies: List[str] = field(default_factory=list)


@dataclass
class AgentMessage:
    """Enhanced message structure for agent communication"""
    id: str
    sender_id: str
    receiver_id: str
    protocol: CommunicationProtocol
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    requires_response: bool = False
    priority: int = 5  # 1-10
    context_data: Optional[Dict[str, Any]] = None


@dataclass
class AgentNode:
    """Represents an agent in the orchestration system"""
    id: str
    agent: Agent
    role: AgentRole
    capabilities: List[AgentCapability]
    status: AgentStatus
    current_task: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    communication_history: List[AgentMessage] = field(default_factory=list)
    trust_score: float = 1.0
    specialization_level: float = 1.0


class AgentOrchestrator:
    """
    Advanced orchestration system for managing multiple specialized agents
    """
    
    def __init__(self, main_agent: Agent):
        self.main_agent = main_agent
        self.agents: Dict[str, AgentNode] = {}
        self.message_queue: List[AgentMessage] = []
        self.active_negotiations: Dict[str, Dict[str, Any]] = {}
        self.shared_context: Dict[str, Any] = {}
        self.performance_history: List[Dict[str, Any]] = []
        self.orchestrator_id = str(uuid.uuid4())
        
    async def register_agent(
        self, 
        agent: Agent, 
        role: AgentRole, 
        capabilities: List[AgentCapability]
    ) -> str:
        """Register a new agent in the orchestration system"""
        agent_id = str(uuid.uuid4())
        
        agent_node = AgentNode(
            id=agent_id,
            agent=agent,
            role=role,
            capabilities=capabilities,
            status=AgentStatus.IDLE
        )
        
        self.agents[agent_id] = agent_node
        
        # Initialize agent with orchestration capabilities
        await self._initialize_agent_orchestration(agent_node)
        
        PrintStyle(font_color="green").print(
            f"🤖 Agent registered: {role.value} ({agent_id[:8]})"
        )
        
        return agent_id
    
    async def create_specialized_agent(
        self, 
        role: AgentRole, 
        task_description: str,
        capabilities: Optional[List[AgentCapability]] = None
    ) -> str:
        """Create and register a new specialized agent"""
        
        # Create new agent with specialized configuration
        config = self.main_agent.config
        context = AgentContext(config=config)
        
        specialized_agent = Agent(
            number=len(self.agents) + 1,
            config=config,
            context=context
        )
        
        # Set specialized profile based on role
        profile_mapping = {
            AgentRole.RESEARCHER: "researcher",
            AgentRole.DEVELOPER: "developer", 
            AgentRole.SECURITY: "hacker",
            AgentRole.ANALYST: "researcher",
            AgentRole.CREATIVE: "default",
            AgentRole.VALIDATOR: "default"
        }
        
        specialized_agent.config.profile = profile_mapping.get(role, "default")
        
        # Define default capabilities if not provided
        if capabilities is None:
            capabilities = await self._get_default_capabilities(role)
        
        # Register the agent
        agent_id = await self.register_agent(specialized_agent, role, capabilities)
        
        # Initialize with task description
        await self._initialize_agent_task(agent_id, task_description)
        
        return agent_id
    
    async def orchestrate_task(
        self, 
        task: str, 
        required_roles: List[AgentRole],
        coordination_strategy: str = "collaborative"
    ) -> Dict[str, Any]:
        """
        Orchestrate a complex task across multiple specialized agents
        """
        
        orchestration_id = str(uuid.uuid4())
        
        PrintStyle(font_color="cyan", bold=True).print(
            f"🎭 Starting orchestration: {orchestration_id[:8]}"
        )
        
        # Log orchestration start
        log_item = self.main_agent.context.log.log(
            type="info",
            heading="🎭 Multi-Agent Orchestration Started",
            content=f"Task: {task}\nRequired roles: {[r.value for r in required_roles]}",
            kvps={"orchestration_id": orchestration_id}
        )
        
        try:
            # 1. Analyze task complexity and requirements
            task_analysis = await self._analyze_task_complexity(task, required_roles)
            
            # 2. Ensure required agents are available
            agent_assignments = await self._assign_agents_to_roles(required_roles, task_analysis)
            
            # 3. Create coordination plan
            coordination_plan = await self._create_coordination_plan(
                task, agent_assignments, coordination_strategy
            )
            
            # 4. Execute coordinated workflow
            results = await self._execute_coordinated_workflow(
                orchestration_id, coordination_plan, log_item
            )
            
            # 5. Synthesize final result
            final_result = await self._synthesize_results(results, task)
            
            log_item.update(
                heading="✅ Multi-Agent Orchestration Completed",
                result=final_result["summary"],
                performance_metrics=final_result["metrics"]
            )
            
            return final_result
            
        except Exception as e:
            log_item.update(
                heading="❌ Multi-Agent Orchestration Failed",
                error=str(e)
            )
            raise
    
    async def negotiate_consensus(
        self, 
        topic: str, 
        participating_agents: List[str],
        consensus_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Facilitate negotiation between agents to reach consensus
        """
        
        negotiation_id = str(uuid.uuid4())
        
        PrintStyle(font_color="yellow").print(
            f"🤝 Starting negotiation: {topic}"
        )
        
        negotiation_data = {
            "id": negotiation_id,
            "topic": topic,
            "participants": participating_agents,
            "rounds": [],
            "consensus_reached": False,
            "final_decision": None
        }
        
        self.active_negotiations[negotiation_id] = negotiation_data
        
        max_rounds = 5
        current_round = 0
        
        while current_round < max_rounds and not negotiation_data["consensus_reached"]:
            current_round += 1
            
            PrintStyle(font_color="yellow").print(
                f"🔄 Negotiation round {current_round}/{max_rounds}"
            )
            
            round_results = await self._conduct_negotiation_round(
                negotiation_id, topic, participating_agents, current_round
            )
            
            negotiation_data["rounds"].append(round_results)
            
            # Check for consensus
            consensus_score = await self._calculate_consensus_score(round_results)
            
            if consensus_score >= consensus_threshold:
                negotiation_data["consensus_reached"] = True
                negotiation_data["final_decision"] = await self._extract_consensus_decision(
                    round_results
                )
                break
        
        if not negotiation_data["consensus_reached"]:
            # Fallback to coordinator decision
            negotiation_data["final_decision"] = await self._coordinator_final_decision(
                negotiation_data, topic
            )
        
        PrintStyle(font_color="green").print(
            f"✅ Negotiation completed: {negotiation_data['final_decision']['summary']}"
        )
        
        return negotiation_data
    
    async def share_context(
        self, 
        context_key: str, 
        context_data: Any,
        target_agents: Optional[List[str]] = None
    ):
        """Share context data between agents"""
        
        self.shared_context[context_key] = {
            "data": context_data,
            "timestamp": datetime.now(timezone.utc),
            "shared_by": self.orchestrator_id,
            "access_count": 0
        }
        
        # Notify relevant agents
        if target_agents:
            for agent_id in target_agents:
                if agent_id in self.agents:
                    await self._notify_agent_context_update(agent_id, context_key)
    
    async def get_shared_context(self, context_key: str, requesting_agent: str) -> Any:
        """Retrieve shared context data"""
        
        if context_key in self.shared_context:
            context_item = self.shared_context[context_key]
            context_item["access_count"] += 1
            context_item["last_accessed_by"] = requesting_agent
            context_item["last_accessed_at"] = datetime.now(timezone.utc)
            
            return context_item["data"]
        
        return None
    
    async def _analyze_task_complexity(
        self, 
        task: str, 
        required_roles: List[AgentRole]
    ) -> Dict[str, Any]:
        """Analyze task to determine complexity and requirements"""
        
        analysis_prompt = f"""
        Analyze this task for multi-agent orchestration:
        
        Task: {task}
        Required roles: {[r.value for r in required_roles]}
        
        Provide analysis in JSON format:
        {{
            "complexity_score": 1-10,
            "estimated_duration": "time estimate",
            "critical_dependencies": ["list of dependencies"],
            "risk_factors": ["potential risks"],
            "success_criteria": ["measurable criteria"],
            "coordination_requirements": "description"
        }}
        """
        
        analysis_result = await self.main_agent.call_utility_model(
            system="You are a task analysis expert. Analyze tasks for multi-agent coordination.",
            message=analysis_prompt
        )
        
        try:
            return json.loads(analysis_result)
        except:
            return {
                "complexity_score": 5,
                "estimated_duration": "unknown",
                "critical_dependencies": [],
                "risk_factors": ["analysis_failed"],
                "success_criteria": ["task_completion"],
                "coordination_requirements": "standard"
            }
    
    async def _assign_agents_to_roles(
        self, 
        required_roles: List[AgentRole],
        task_analysis: Dict[str, Any]
    ) -> Dict[AgentRole, str]:
        """Assign available agents to required roles"""
        
        assignments = {}
        
        for role in required_roles:
            # Find best available agent for this role
            best_agent = await self._find_best_agent_for_role(role, task_analysis)
            
            if best_agent:
                assignments[role] = best_agent
                self.agents[best_agent].status = AgentStatus.WORKING
            else:
                # Create new specialized agent if none available
                new_agent_id = await self.create_specialized_agent(
                    role, 
                    f"Specialized {role.value} for current orchestration"
                )
                assignments[role] = new_agent_id
        
        return assignments
    
    async def _find_best_agent_for_role(
        self, 
        role: AgentRole, 
        task_analysis: Dict[str, Any]
    ) -> Optional[str]:
        """Find the best available agent for a specific role"""
        
        candidates = [
            agent_node for agent_node in self.agents.values()
            if agent_node.role == role and agent_node.status == AgentStatus.IDLE
        ]
        
        if not candidates:
            return None
        
        # Score candidates based on performance and specialization
        best_candidate = max(
            candidates,
            key=lambda x: (
                x.trust_score * 0.4 + 
                x.specialization_level * 0.3 + 
                x.performance_metrics.get("success_rate", 0.5) * 0.3
            )
        )
        
        return best_candidate.id
    
    async def _create_coordination_plan(
        self,
        task: str,
        agent_assignments: Dict[AgentRole, str],
        strategy: str
    ) -> Dict[str, Any]:
        """Create detailed coordination plan"""
        
        plan = {
            "strategy": strategy,
            "phases": [],
            "dependencies": {},
            "communication_flow": {},
            "success_metrics": {},
            "fallback_plans": {}
        }
        
        # Define coordination strategies
        if strategy == "collaborative":
            plan = await self._create_collaborative_plan(task, agent_assignments)
        elif strategy == "sequential":
            plan = await self._create_sequential_plan(task, agent_assignments)
        elif strategy == "parallel":
            plan = await self._create_parallel_plan(task, agent_assignments)
        else:
            plan = await self._create_adaptive_plan(task, agent_assignments)
        
        return plan
    
    async def _create_collaborative_plan(
        self, 
        task: str, 
        assignments: Dict[AgentRole, str]
    ) -> Dict[str, Any]:
        """Create collaborative coordination plan"""
        
        return {
            "strategy": "collaborative",
            "phases": [
                {
                    "name": "initialization",
                    "participants": list(assignments.values()),
                    "objective": "Share context and establish common understanding",
                    "duration_estimate": 60
                },
                {
                    "name": "parallel_work",
                    "participants": list(assignments.values()),
                    "objective": "Work on assigned aspects simultaneously",
                    "duration_estimate": 300
                },
                {
                    "name": "integration",
                    "participants": list(assignments.values()),
                    "objective": "Integrate results and resolve conflicts",
                    "duration_estimate": 120
                },
                {
                    "name": "validation",
                    "participants": [assignments.get(AgentRole.VALIDATOR, list(assignments.values())[0])],
                    "objective": "Validate final result",
                    "duration_estimate": 60
                }
            ],
            "communication_flow": {
                "type": "mesh",
                "frequency": "continuous",
                "protocols": [CommunicationProtocol.DIRECT, CommunicationProtocol.BROADCAST]
            }
        }
    
    async def _execute_coordinated_workflow(
        self,
        orchestration_id: str,
        plan: Dict[str, Any],
        log_item: LogItem
    ) -> Dict[str, Any]:
        """Execute the coordinated workflow"""
        
        results = {
            "orchestration_id": orchestration_id,
            "phase_results": {},
            "agent_contributions": {},
            "performance_metrics": {},
            "timeline": []
        }
        
        for phase in plan["phases"]:
            phase_start = datetime.now(timezone.utc)
            
            log_item.update(
                progress=f"Executing phase: {phase['name']}",
                current_phase=phase['name']
            )
            
            PrintStyle(font_color="blue").print(
                f"🔄 Phase: {phase['name']} - {phase['objective']}"
            )
            
            phase_result = await self._execute_phase(phase, plan)
            
            results["phase_results"][phase["name"]] = phase_result
            results["timeline"].append({
                "phase": phase["name"],
                "start_time": phase_start,
                "end_time": datetime.now(timezone.utc),
                "duration": (datetime.now(timezone.utc) - phase_start).total_seconds(),
                "success": phase_result.get("success", False)
            })
            
            # Update shared context with phase results
            await self.share_context(
                f"phase_{phase['name']}_result",
                phase_result,
                phase.get("participants", [])
            )
        
        return results
    
    async def _execute_phase(self, phase: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single phase of the coordination plan"""
        
        participants = phase.get("participants", [])
        objective = phase.get("objective", "")
        
        if phase["name"] == "parallel_work":
            # Execute tasks in parallel
            tasks = []
            for agent_id in participants:
                if agent_id in self.agents:
                    task = asyncio.create_task(
                        self._execute_agent_task(agent_id, objective)
                    )
                    tasks.append((agent_id, task))
            
            # Wait for all tasks to complete
            results = {}
            for agent_id, task in tasks:
                try:
                    result = await task
                    results[agent_id] = result
                except Exception as e:
                    results[agent_id] = {"error": str(e), "success": False}
            
            return {"type": "parallel", "results": results, "success": True}
        
        else:
            # Execute tasks sequentially
            results = {}
            for agent_id in participants:
                if agent_id in self.agents:
                    result = await self._execute_agent_task(agent_id, objective)
                    results[agent_id] = result
                    
                    # Share intermediate results
                    await self.share_context(
                        f"intermediate_{agent_id}",
                        result,
                        participants
                    )
            
            return {"type": "sequential", "results": results, "success": True}
    
    async def _execute_agent_task(self, agent_id: str, objective: str) -> Dict[str, Any]:
        """Execute a task on a specific agent"""
        
        if agent_id not in self.agents:
            return {"error": "Agent not found", "success": False}
        
        agent_node = self.agents[agent_id]
        agent_node.status = AgentStatus.WORKING
        
        try:
            # Prepare enhanced context for the agent
            enhanced_context = await self._prepare_agent_context(agent_id, objective)
            
            # Create specialized message for the agent
            specialized_message = await self._create_specialized_message(
                agent_node.role, objective, enhanced_context
            )
            
            # Execute task on agent
            start_time = datetime.now(timezone.utc)
            
            # Add user message to agent
            agent_node.agent.hist_add_user_message(
                UserMessage(message=specialized_message)
            )
            
            # Run agent monologue
            result = await agent_node.agent.monologue()
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            # Update performance metrics
            await self._update_agent_performance(agent_id, duration, True)
            
            agent_node.status = AgentStatus.COMPLETED
            
            return {
                "agent_id": agent_id,
                "role": agent_node.role.value,
                "result": result,
                "duration": duration,
                "success": True,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            agent_node.status = AgentStatus.ERROR
            await self._update_agent_performance(agent_id, 0, False)
            
            return {
                "agent_id": agent_id,
                "role": agent_node.role.value,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _prepare_agent_context(self, agent_id: str, objective: str) -> Dict[str, Any]:
        """Prepare enhanced context for agent execution"""
        
        agent_node = self.agents[agent_id]
        
        context = {
            "orchestration_role": agent_node.role.value,
            "current_objective": objective,
            "shared_context": self.shared_context,
            "peer_agents": [
                {
                    "id": aid,
                    "role": anode.role.value,
                    "status": anode.status.value,
                    "capabilities": [cap.name for cap in anode.capabilities]
                }
                for aid, anode in self.agents.items() if aid != agent_id
            ],
            "performance_expectations": {
                "quality_threshold": 0.8,
                "time_budget": 300,
                "collaboration_required": True
            }
        }
        
        return context
    
    async def _create_specialized_message(
        self, 
        role: AgentRole, 
        objective: str, 
        context: Dict[str, Any]
    ) -> str:
        """Create specialized message based on agent role"""
        
        role_instructions = {
            AgentRole.RESEARCHER: "As a research specialist, focus on gathering comprehensive information, analyzing data, and providing evidence-based insights.",
            AgentRole.DEVELOPER: "As a development specialist, focus on creating robust, scalable solutions with clean code and proper documentation.",
            AgentRole.ANALYST: "As an analysis specialist, focus on data interpretation, pattern recognition, and strategic recommendations.",
            AgentRole.SECURITY: "As a security specialist, focus on identifying vulnerabilities, implementing protections, and ensuring compliance.",
            AgentRole.CREATIVE: "As a creative specialist, focus on innovative solutions, user experience, and engaging content.",
            AgentRole.VALIDATOR: "As a validation specialist, focus on quality assurance, testing, and verification of results."
        }
        
        base_instruction = role_instructions.get(
            role, 
            "As a specialized agent, focus on your area of expertise."
        )
        
        message = f"""
{base_instruction}

CURRENT OBJECTIVE: {objective}

ORCHESTRATION CONTEXT:
- You are part of a multi-agent collaboration
- Other agents are working on related aspects
- Share relevant findings and coordinate when beneficial
- Maintain high quality standards

SHARED CONTEXT AVAILABLE:
{json.dumps(context.get('shared_context', {}), indent=2)}

PEER AGENTS:
{json.dumps(context.get('peer_agents', []), indent=2)}

Execute your specialized role while contributing to the overall objective.
"""
        
        return message
    
    async def _synthesize_results(
        self, 
        results: Dict[str, Any], 
        original_task: str
    ) -> Dict[str, Any]:
        """Synthesize results from all agents into final output"""
        
        # Collect all agent contributions
        contributions = []
        for phase_name, phase_result in results["phase_results"].items():
            if "results" in phase_result:
                for agent_id, agent_result in phase_result["results"].items():
                    if agent_result.get("success") and "result" in agent_result:
                        contributions.append({
                            "agent_id": agent_id,
                            "role": self.agents[agent_id].role.value,
                            "phase": phase_name,
                            "contribution": agent_result["result"]
                        })
        
        # Use main agent to synthesize final result
        synthesis_prompt = f"""
        Synthesize the following multi-agent contributions into a comprehensive final result:
        
        ORIGINAL TASK: {original_task}
        
        AGENT CONTRIBUTIONS:
        {json.dumps(contributions, indent=2)}
        
        ORCHESTRATION TIMELINE:
        {json.dumps(results["timeline"], indent=2)}
        
        Provide a comprehensive synthesis that:
        1. Integrates all valuable contributions
        2. Resolves any conflicts or contradictions
        3. Presents a coherent final result
        4. Highlights the collaborative process value
        """
        
        synthesis = await self.main_agent.call_utility_model(
            system="You are a synthesis expert. Integrate multi-agent results into coherent outputs.",
            message=synthesis_prompt
        )
        
        # Calculate performance metrics
        total_duration = sum(
            timeline["duration"] for timeline in results["timeline"]
        )
        
        success_rate = sum(
            1 for timeline in results["timeline"] if timeline["success"]
        ) / len(results["timeline"]) if results["timeline"] else 0
        
        return {
            "synthesis": synthesis,
            "summary": f"Multi-agent orchestration completed with {len(contributions)} contributions",
            "original_task": original_task,
            "contributions": contributions,
            "metrics": {
                "total_duration": total_duration,
                "success_rate": success_rate,
                "agents_involved": len(set(c["agent_id"] for c in contributions)),
                "phases_completed": len(results["phase_results"])
            },
            "orchestration_id": results["orchestration_id"]
        }
    
    async def _get_default_capabilities(self, role: AgentRole) -> List[AgentCapability]:
        """Get default capabilities for each role"""
        
        capabilities_map = {
            AgentRole.RESEARCHER: [
                AgentCapability(
                    name="web_research",
                    description="Comprehensive web research and analysis",
                    input_schema={"query": "string", "depth": "integer"},
                    output_schema={"findings": "array", "sources": "array"},
                    complexity_level=6,
                    estimated_time=180
                ),
                AgentCapability(
                    name="data_analysis",
                    description="Statistical and qualitative data analysis",
                    input_schema={"data": "object", "analysis_type": "string"},
                    output_schema={"insights": "array", "visualizations": "array"},
                    complexity_level=7,
                    estimated_time=240
                )
            ],
            AgentRole.DEVELOPER: [
                AgentCapability(
                    name="code_development",
                    description="Full-stack software development",
                    input_schema={"requirements": "string", "tech_stack": "array"},
                    output_schema={"code": "string", "documentation": "string"},
                    complexity_level=8,
                    estimated_time=600
                ),
                AgentCapability(
                    name="system_architecture",
                    description="Design system architecture and infrastructure",
                    input_schema={"requirements": "object", "constraints": "array"},
                    output_schema={"architecture": "object", "diagrams": "array"},
                    complexity_level=9,
                    estimated_time=480
                )
            ],
            AgentRole.SECURITY: [
                AgentCapability(
                    name="security_audit",
                    description="Comprehensive security assessment",
                    input_schema={"target": "string", "scope": "array"},
                    output_schema={"vulnerabilities": "array", "recommendations": "array"},
                    complexity_level=8,
                    estimated_time=360
                ),
                AgentCapability(
                    name="penetration_testing",
                    description="Ethical penetration testing",
                    input_schema={"target": "string", "methodology": "string"},
                    output_schema={"findings": "array", "report": "string"},
                    complexity_level=9,
                    estimated_time=720
                )
            ]
        }
        
        return capabilities_map.get(role, [
            AgentCapability(
                name="general_assistance",
                description="General purpose assistance",
                input_schema={"task": "string"},
                output_schema={"result": "string"},
                complexity_level=5,
                estimated_time=120
            )
        ])
    
    async def _initialize_agent_orchestration(self, agent_node: AgentNode):
        """Initialize agent with orchestration capabilities"""
        
        # Add orchestration data to agent
        agent_node.agent.set_data("orchestration_id", self.orchestrator_id)
        agent_node.agent.set_data("agent_node_id", agent_node.id)
        agent_node.agent.set_data("orchestrator", self)
        
        # Initialize performance tracking
        agent_node.performance_metrics = {
            "tasks_completed": 0,
            "success_rate": 1.0,
            "average_duration": 0,
            "quality_score": 1.0,
            "collaboration_score": 1.0
        }
    
    async def _initialize_agent_task(self, agent_id: str, task_description: str):
        """Initialize agent with specific task"""
        
        if agent_id in self.agents:
            agent_node = self.agents[agent_id]
            agent_node.current_task = task_description
            
            # Add task context to agent's memory
            db = await memory.Memory.get(agent_node.agent)
            await db.insert_text(
                f"Orchestration Task Assignment: {task_description}",
                {"area": "main", "type": "orchestration_task"}
            )
    
    async def _update_agent_performance(
        self, 
        agent_id: str, 
        duration: float, 
        success: bool
    ):
        """Update agent performance metrics"""
        
        if agent_id not in self.agents:
            return
        
        agent_node = self.agents[agent_id]
        metrics = agent_node.performance_metrics
        
        # Update metrics
        metrics["tasks_completed"] += 1
        
        # Update success rate (exponential moving average)
        alpha = 0.1
        metrics["success_rate"] = (
            alpha * (1.0 if success else 0.0) + 
            (1 - alpha) * metrics["success_rate"]
        )
        
        # Update average duration
        if success:
            metrics["average_duration"] = (
                (metrics["average_duration"] * (metrics["tasks_completed"] - 1) + duration) /
                metrics["tasks_completed"]
            )
        
        # Update trust score based on performance
        agent_node.trust_score = min(1.0, metrics["success_rate"] * 1.1)
    
    async def _conduct_negotiation_round(
        self,
        negotiation_id: str,
        topic: str,
        participants: List[str],
        round_number: int
    ) -> Dict[str, Any]:
        """Conduct a single round of negotiation"""
        
        round_results = {
            "round": round_number,
            "positions": {},
            "arguments": {},
            "compromises": {},
            "agreements": {}
        }
        
        # Get each agent's position
        for agent_id in participants:
            if agent_id in self.agents:
                agent_node = self.agents[agent_id]
                
                negotiation_prompt = f"""
                NEGOTIATION ROUND {round_number}
                
                Topic: {topic}
                
                Your role: {agent_node.role.value}
                
                Previous rounds: {json.dumps(self.active_negotiations[negotiation_id]["rounds"], indent=2)}
                
                Provide your position in JSON format:
                {{
                    "position": "your stance on the topic",
                    "arguments": ["supporting arguments"],
                    "compromises": ["what you're willing to compromise on"],
                    "requirements": ["non-negotiable requirements"]
                }}
                """
                
                try:
                    response = await agent_node.agent.call_utility_model(
                        system=f"You are a {agent_node.role.value} agent participating in a negotiation. Be professional and collaborative.",
                        message=negotiation_prompt
                    )
                    
                    position = json.loads(response)
                    round_results["positions"][agent_id] = position
                    
                except Exception as e:
                    round_results["positions"][agent_id] = {
                        "error": str(e),
                        "position": "unable to participate"
                    }
        
        return round_results
    
    async def _calculate_consensus_score(self, round_results: Dict[str, Any]) -> float:
        """Calculate consensus score for negotiation round"""
        
        positions = round_results.get("positions", {})
        
        if len(positions) < 2:
            return 0.0
        
        # Simple consensus calculation based on agreement keywords
        agreement_keywords = ["agree", "accept", "support", "approve", "consensus"]
        disagreement_keywords = ["disagree", "reject", "oppose", "conflict"]
        
        total_score = 0
        valid_positions = 0
        
        for agent_id, position in positions.items():
            if "error" in position:
                continue
                
            valid_positions += 1
            position_text = json.dumps(position).lower()
            
            agreement_count = sum(
                position_text.count(keyword) for keyword in agreement_keywords
            )
            disagreement_count = sum(
                position_text.count(keyword) for keyword in disagreement_keywords
            )
            
            if agreement_count > disagreement_count:
                total_score += 1
            elif agreement_count == disagreement_count:
                total_score += 0.5
        
        return total_score / valid_positions if valid_positions > 0 else 0.0
    
    async def _extract_consensus_decision(self, round_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract consensus decision from negotiation round"""
        
        positions = round_results.get("positions", {})
        
        # Use main agent to synthesize consensus
        synthesis_prompt = f"""
        Extract the consensus decision from these agent positions:
        
        {json.dumps(positions, indent=2)}
        
        Provide the consensus in JSON format:
        {{
            "decision": "the agreed upon decision",
            "summary": "brief summary of the consensus",
            "supporting_agents": ["list of agent IDs that support this"],
            "key_points": ["main points of agreement"],
            "implementation_steps": ["steps to implement the decision"]
        }}
        """
        
        consensus_result = await self.main_agent.call_utility_model(
            system="You are a consensus extraction expert. Identify common ground and agreements.",
            message=synthesis_prompt
        )
        
        try:
            return json.loads(consensus_result)
        except:
            return {
                "decision": "consensus extraction failed",
                "summary": "Unable to extract clear consensus",
                "supporting_agents": [],
                "key_points": [],
                "implementation_steps": []
            }
    
    async def _coordinator_final_decision(
        self, 
        negotiation_data: Dict[str, Any], 
        topic: str
    ) -> Dict[str, Any]:
        """Make final decision when consensus cannot be reached"""
        
        decision_prompt = f"""
        As the coordinator, make a final decision on this topic where consensus was not reached:
        
        Topic: {topic}
        
        Negotiation history: {json.dumps(negotiation_data["rounds"], indent=2)}
        
        Provide your decision in JSON format:
        {{
            "decision": "your final decision",
            "rationale": "reasoning behind the decision",
            "implementation_plan": ["steps to implement"],
            "risk_mitigation": ["how to address concerns raised"]
        }}
        """
        
        decision_result = await self.main_agent.call_utility_model(
            system="You are a coordinator making final decisions. Be fair and consider all perspectives.",
            message=decision_prompt
        )
        
        try:
            decision = json.loads(decision_result)
            decision["type"] = "coordinator_decision"
            decision["consensus_reached"] = False
            return decision
        except:
            return {
                "decision": "maintain status quo",
                "rationale": "Unable to process decision criteria",
                "type": "coordinator_decision",
                "consensus_reached": False
            }
    
    async def _notify_agent_context_update(self, agent_id: str, context_key: str):
        """Notify agent of context update"""
        
        if agent_id in self.agents:
            agent_node = self.agents[agent_id]
            
            # Add context update to agent's memory
            db = await memory.Memory.get(agent_node.agent)
            await db.insert_text(
                f"Shared context updated: {context_key}",
                {"area": "main", "type": "context_update", "context_key": context_key}
            )
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status"""
        
        return {
            "orchestrator_id": self.orchestrator_id,
            "total_agents": len(self.agents),
            "agents_by_status": {
                status.value: len([
                    a for a in self.agents.values() 
                    if a.status == status
                ]) for status in AgentStatus
            },
            "agents_by_role": {
                role.value: len([
                    a for a in self.agents.values() 
                    if a.role == role
                ]) for role in AgentRole
            },
            "active_negotiations": len(self.active_negotiations),
            "shared_context_items": len(self.shared_context),
            "message_queue_size": len(self.message_queue)
        }
    
    async def save_orchestration_state(self):
        """Save orchestration state for persistence"""
        
        state = {
            "orchestrator_id": self.orchestrator_id,
            "agents": {
                agent_id: {
                    "role": node.role.value,
                    "status": node.status.value,
                    "capabilities": [
                        {
                            "name": cap.name,
                            "description": cap.description,
                            "complexity_level": cap.complexity_level
                        } for cap in node.capabilities
                    ],
                    "performance_metrics": node.performance_metrics,
                    "trust_score": node.trust_score
                } for agent_id, node in self.agents.items()
            },
            "shared_context": self.shared_context,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to file
        state_file = files.get_abs_path("tmp", "orchestration_state.json")
        files.write_file(state_file, json.dumps(state, indent=2))
        
        return state_file


# Global orchestrator instance
_global_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator(main_agent: Agent) -> AgentOrchestrator:
    """Get or create global orchestrator instance"""
    global _global_orchestrator
    
    if _global_orchestrator is None:
        _global_orchestrator = AgentOrchestrator(main_agent)
    
    return _global_orchestrator


def reset_orchestrator():
    """Reset global orchestrator (for testing/cleanup)"""
    global _global_orchestrator
    _global_orchestrator = None