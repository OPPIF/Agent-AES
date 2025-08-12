"""
Contextual Analysis Tool
Provides advanced semantic analysis and intent detection
"""

import json
from python.helpers.tool import Tool, Response
from python.helpers.contextual_intelligence import (
    get_contextual_intelligence, IntentType, ContextualComplexity, EmotionalTone
)
from python.helpers.print_style import PrintStyle


class ContextualAnalysis(Tool):
    """
    Tool for advanced contextual analysis of user messages and conversations
    """
    
    async def execute(self, **kwargs):
        action = kwargs.get("action", "analyze")
        message = kwargs.get("message", "")
        
        if action == "analyze":
            return await self._analyze_message(kwargs)
        elif action == "predict":
            return await self._predict_needs(kwargs)
        elif action == "profile":
            return await self._get_user_profile(kwargs)
        elif action == "patterns":
            return await self._analyze_patterns()
        elif action == "suggestions":
            return await self._get_suggestions(kwargs)
        else:
            return Response(
                message=f"Error: Unknown action '{action}'. Available: analyze, predict, profile, patterns, suggestions",
                break_loop=False
            )
    
    async def _analyze_message(self, kwargs) -> Response:
        """Analyze a specific message for intent and context"""
        
        message = kwargs.get("message", "")
        include_history = kwargs.get("include_history", True)
        
        if not message:
            return Response(
                message="Error: Message is required for analysis",
                break_loop=False
            )
        
        try:
            intelligence = get_contextual_intelligence(self.agent)
            
            # Get conversation history if requested
            history = ""
            if include_history:
                history = self.agent.concat_messages(start=-10)  # Last 10 messages
            
            # Perform analysis
            intent_analysis = await intelligence.analyze_intent(message, history)
            
            # Get recommendations
            recommendations = await intelligence.get_contextual_recommendations(message, history)
            
            response_text = f"""
# 🧠 Advanced Contextual Analysis

## Message Analyzed
"{message}"

## Intent Analysis
- **Primary Intent**: {intent_analysis.primary_intent.value.title()}
- **Confidence**: {intent_analysis.confidence:.1%}
- **Complexity Level**: {intent_analysis.complexity.value}/5 ({intent_analysis.complexity.name})
- **Emotional Tone**: {intent_analysis.emotional_tone.value.title()}

## Semantic Entities Detected
"""
            
            if intent_analysis.entities:
                for entity in intent_analysis.entities:
                    response_text += f"- **{entity.entity_type.title()}**: {entity.text} (confidence: {entity.confidence:.1%})\n"
            else:
                response_text += "- No specific entities detected\n"
            
            response_text += f"""
## Keywords Extracted
{', '.join(intent_analysis.keywords[:10]) if intent_analysis.keywords else 'None'}

## Context Requirements
{', '.join(intent_analysis.context_requirements) if intent_analysis.context_requirements else 'None'}

## Predicted Follow-up
{intent_analysis.predicted_followup or 'No prediction available'}

## Contextual Suggestions
"""
            
            for suggestion in recommendations.get("suggestions", []):
                response_text += f"""
### {suggestion['title']} (Priority: {suggestion['priority']}/10)
{suggestion['description']}
**Action**: `{suggestion['action']}`

"""
            
            return Response(message=response_text, break_loop=False)
            
        except Exception as e:
            return Response(
                message=f"Analysis failed: {str(e)}",
                break_loop=False
            )
    
    async def _predict_needs(self, kwargs) -> Response:
        """Predict user needs based on context"""
        
        try:
            intelligence = get_contextual_intelligence(self.agent)
            
            # Build current context
            current_context = {
                "recent_messages": self.agent.concat_messages(start=-5),
                "current_time": datetime.now().isoformat(),
                "agent_state": "active"
            }
            
            # Get predictions
            predictions = await intelligence.predict_user_needs(current_context)
            
            response_text = f"""
# 🔮 Predictive Intelligence Analysis

## Immediate Needs (Confidence: {predictions.get('confidence_score', 0):.1%})
"""
            
            for need in predictions.get("immediate_needs", []):
                response_text += f"- {need}\n"
            
            response_text += f"""
## Upcoming Tasks Predicted
"""
            
            for task in predictions.get("upcoming_tasks", []):
                response_text += f"- {task}\n"
            
            response_text += f"""
## Potential Blockers
"""
            
            for blocker in predictions.get("potential_blockers", []):
                response_text += f"- ⚠️ {blocker}\n"
            
            response_text += f"""
## Proactive Suggestions
"""
            
            for suggestion in predictions.get("suggested_actions", []):
                response_text += f"- 💡 {suggestion}\n"
            
            response_text += f"""
## Resource Requirements
"""
            
            for resource in predictions.get("resource_requirements", []):
                response_text += f"- 📋 {resource}\n"
            
            response_text += f"""
## Reasoning
{predictions.get('reasoning', 'No reasoning provided')}
"""
            
            return Response(message=response_text, break_loop=False)
            
        except Exception as e:
            return Response(
                message=f"Prediction failed: {str(e)}",
                break_loop=False
            )
    
    async def _get_user_profile(self, kwargs) -> Response:
        """Get dynamic user profile"""
        
        try:
            intelligence = get_contextual_intelligence(self.agent)
            user_id = kwargs.get("user_id", "default")
            
            profile = await intelligence.build_user_profile(user_id)
            
            response_text = f"""
# 👤 Dynamic User Profile

## User ID
{profile.user_id}

## Communication Style
**{profile.communication_style.title()}** - Adapted based on interaction complexity

## Expertise Areas (Top 10)
"""
            
            for i, area in enumerate(profile.expertise_areas[:10], 1):
                response_text += f"{i}. {area}\n"
            
            response_text += f"""
## Typical Task Types
"""
            
            for task in profile.typical_tasks:
                response_text += f"- {task.replace('_', ' ').title()}\n"
            
            response_text += f"""
## Learning Patterns
"""
            
            for pattern, score in sorted(profile.learning_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
                response_text += f"- **{pattern.replace('_', ' ').title()}**: {score:.1%} success rate\n"
            
            response_text += f"""
## Profile Statistics
- **Total Interactions**: {len(profile.interaction_history)}
- **Last Updated**: {profile.last_updated.strftime('%Y-%m-%d %H:%M:%S')}
- **Profile Age**: {(datetime.now(timezone.utc) - profile.last_updated).days} days

## Recent Interaction Trends
"""
            
            if profile.interaction_history:
                recent = profile.interaction_history[-10:]
                intent_counts = {}
                for interaction in recent:
                    intent = interaction.get("intent", "unknown")
                    intent_counts[intent] = intent_counts.get(intent, 0) + 1
                
                for intent, count in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True):
                    response_text += f"- **{intent.replace('_', ' ').title()}**: {count} times\n"
            
            return Response(message=response_text, break_loop=False)
            
        except Exception as e:
            return Response(
                message=f"Profile analysis failed: {str(e)}",
                break_loop=False
            )
    
    async def _analyze_patterns(self) -> Response:
        """Analyze conversation patterns"""
        
        try:
            intelligence = get_contextual_intelligence(self.agent)
            patterns = await intelligence.analyze_conversation_patterns()
            
            if not patterns:
                return Response(
                    message="No conversation patterns detected yet. More interactions needed for pattern analysis.",
                    break_loop=False
                )
            
            response_text = f"""
# 📈 Conversation Pattern Analysis

## Detected Patterns ({len(patterns)} total)
"""
            
            for pattern_type, pattern in sorted(patterns.items(), key=lambda x: x[1].frequency, reverse=True):
                response_text += f"""
### {pattern_type.replace('->', ' → ').replace('_', ' ').title()}
- **Frequency**: {pattern.frequency} occurrences
- **Success Rate**: {pattern.success_rate:.1%}
- **Typical Duration**: {pattern.typical_duration:.1f} seconds
- **Last Seen**: {pattern.last_occurrence.strftime('%Y-%m-%d %H:%M')}

"""
            
            response_text += f"""
## Pattern Insights
- **Most Common**: {max(patterns.items(), key=lambda x: x[1].frequency)[0] if patterns else 'None'}
- **Most Successful**: {max(patterns.items(), key=lambda x: x[1].success_rate)[0] if patterns else 'None'}
- **Total Pattern Types**: {len(patterns)}

## Recommendations
Based on these patterns, consider:
- Optimizing workflows for common patterns
- Creating templates for frequent sequences
- Automating repetitive pattern chains
"""
            
            return Response(message=response_text, break_loop=False)
            
        except Exception as e:
            return Response(
                message=f"Pattern analysis failed: {str(e)}",
                break_loop=False
            )
    
    async def _get_suggestions(self, kwargs) -> Response:
        """Get contextual suggestions for current situation"""
        
        message = kwargs.get("message", "")
        
        if not message:
            # Use last user message if no message provided
            if self.agent.last_user_message:
                content = self.agent.last_user_message.content
                if isinstance(content, dict):
                    message = content.get("user_message", "")
                elif isinstance(content, str):
                    message = content
        
        if not message:
            return Response(
                message="Error: No message provided and no recent user message found",
                break_loop=False
            )
        
        try:
            intelligence = get_contextual_intelligence(self.agent)
            
            # Get conversation history
            history = self.agent.concat_messages(start=-10)
            
            # Get recommendations
            recommendations = await intelligence.get_contextual_recommendations(message, history)
            
            response_text = f"""
# 💡 Contextual Suggestions

## For Message: "{message[:100]}{'...' if len(message) > 100 else ''}"

## Intent-Based Suggestions
"""
            
            for suggestion in recommendations.get("suggestions", []):
                priority_bar = "🔥" * (suggestion["priority"] // 2)
                response_text += f"""
### {suggestion['title']} {priority_bar}
**Type**: {suggestion['type'].replace('_', ' ').title()}
**Description**: {suggestion['description']}
**Recommended Action**: `{suggestion['action']}`

"""
            
            response_text += f"""
## Predictive Insights
"""
            
            predictions = recommendations.get("predictions", {})
            if predictions.get("immediate_needs"):
                response_text += "**Immediate Needs**:\n"
                for need in predictions["immediate_needs"][:3]:
                    response_text += f"- {need}\n"
            
            if predictions.get("upcoming_tasks"):
                response_text += "\n**Likely Next Tasks**:\n"
                for task in predictions["upcoming_tasks"][:3]:
                    response_text += f"- {task}\n"
            
            response_text += f"""
## User Profile Context
- **Communication Style**: {recommendations.get('user_profile', {}).get('communication_style', 'Unknown')}
- **Expertise Areas**: {', '.join(recommendations.get('user_profile', {}).get('expertise_areas', [])[:3])}
- **Typical Tasks**: {', '.join(recommendations.get('user_profile', {}).get('typical_tasks', []))}
"""
            
            return Response(message=response_text, break_loop=False)
            
        except Exception as e:
            return Response(
                message=f"Suggestions failed: {str(e)}",
                break_loop=False
            )