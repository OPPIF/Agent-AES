### negotiate_consensus:
Facilitate negotiation and consensus building between specialized agents
Enables democratic decision-making and conflict resolution in multi-agent scenarios
Supports complex discussions requiring multiple perspectives and expertise

**Arguments:**
- topic (string): The topic or decision that requires consensus
- agents (array): List of agent identifiers or roles to participate in negotiation
- threshold (float): Consensus threshold (0.0-1.0, default 0.7 = 70% agreement)

**Example usage:**
```json
{
    "thoughts": [
        "This decision requires input from multiple specialized perspectives",
        "I need to facilitate a negotiation between different agent viewpoints",
        "A consensus approach will ensure the best possible outcome"
    ],
    "headline": "Facilitating agent consensus negotiation",
    "tool_name": "negotiate_consensus",
    "tool_args": {
        "topic": "Choose the optimal database architecture for high-traffic application: SQL vs NoSQL vs Hybrid approach",
        "agents": ["developer", "analyst", "security"],
        "threshold": 0.8
    }
}
```

**Negotiation Features:**
- Multi-round negotiation process with structured arguments
- Automatic consensus detection and scoring
- Fallback to coordinator decision if consensus cannot be reached
- Detailed negotiation history and rationale tracking
- Support for complex multi-faceted decisions
- Integration with shared context system for informed discussions