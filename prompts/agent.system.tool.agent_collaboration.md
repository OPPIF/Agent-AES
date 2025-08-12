### agent_collaboration:
Manage collaborative workflows and communication between agents
Provides advanced coordination capabilities for multi-agent scenarios
Enables context sharing, team creation, and collaboration monitoring

**Arguments:**
- action (string): Action to perform - "status", "create_team", "share_context", "get_context", "list_agents"
- Additional arguments based on action:

**For action "create_team":**
- team_name (string): Name for the agent team
- roles (array): List of agent roles for team members
- purpose (string): Purpose and objectives of the team

**For action "share_context":**
- context_key (string): Unique identifier for the shared context
- context_data (string/object): Data to share between agents
- target_agents (array, optional): Specific agents to share with (default: all)

**For action "get_context":**
- context_key (string): Key of the context to retrieve

**Example usage - Get Status:**
```json
{
    "thoughts": [
        "I need to check the current state of agent orchestration",
        "This will show me available agents and their performance"
    ],
    "headline": "Checking agent collaboration status",
    "tool_name": "agent_collaboration",
    "tool_args": {
        "action": "status"
    }
}
```

**Example usage - Create Team:**
```json
{
    "thoughts": [
        "I need to create a specialized team for this complex project",
        "Different roles will bring different expertise to the task"
    ],
    "headline": "Creating specialized agent team",
    "tool_name": "agent_collaboration",
    "tool_args": {
        "action": "create_team",
        "team_name": "Security Assessment Team",
        "roles": ["security", "developer", "analyst"],
        "purpose": "Comprehensive security audit of web application"
    }
}
```

**Example usage - Share Context:**
```json
{
    "thoughts": [
        "I need to share important findings with other agents",
        "This context will help them make better decisions"
    ],
    "headline": "Sharing context with agent team",
    "tool_name": "agent_collaboration",
    "tool_args": {
        "action": "share_context",
        "context_key": "security_findings",
        "context_data": "{\"vulnerabilities\": [\"SQL injection\", \"XSS\"], \"severity\": \"high\"}",
        "target_agents": ["developer", "analyst"]
    }
}
```

**Collaboration Features:**
- Real-time agent status monitoring
- Dynamic team creation with specialized roles
- Secure context sharing between agents
- Performance tracking and optimization
- Trust scoring and reliability metrics
- Automatic workload balancing