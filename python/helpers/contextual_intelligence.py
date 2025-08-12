"""
Advanced Contextual Intelligence System
Provides semantic analysis, intent detection, and predictive capabilities
"""

import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter

from python.helpers.memory import Memory
from python.helpers.print_style import PrintStyle
from python.helpers import dirty_json
from python.helpers.log import LogItem
from agent import Agent


class IntentType(Enum):
    """Types of user intentions"""
    QUESTION = "question"
    TASK = "task"
    COMMAND = "command"
    EXPLORATION = "exploration"
    PROBLEM_SOLVING = "problem_solving"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    LEARNING = "learning"
    AUTOMATION = "automation"
    COLLABORATION = "collaboration"


class ContextualComplexity(Enum):
    """Complexity levels for contextual analysis"""
    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3
    EXPERT = 4
    REVOLUTIONARY = 5


class EmotionalTone(Enum):
    """Emotional tone detection"""
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    URGENT = "urgent"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONFUSED = "confused"
    CONFIDENT = "confident"


@dataclass
class SemanticEntity:
    """Represents a semantic entity in text"""
    text: str
    entity_type: str
    confidence: float
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentAnalysis:
    """Results of intent analysis"""
    primary_intent: IntentType
    secondary_intents: List[IntentType]
    confidence: float
    complexity: ContextualComplexity
    emotional_tone: EmotionalTone
    entities: List[SemanticEntity]
    keywords: List[str]
    context_requirements: List[str]
    predicted_followup: Optional[str] = None


@dataclass
class ConversationPattern:
    """Detected conversation patterns"""
    pattern_type: str
    frequency: int
    last_occurrence: datetime
    success_rate: float
    typical_duration: float
    common_followups: List[str]


@dataclass
class UserProfile:
    """Dynamic user profile based on interactions"""
    user_id: str
    preferences: Dict[str, Any]
    expertise_areas: List[str]
    communication_style: str
    typical_tasks: List[str]
    learning_patterns: Dict[str, float]
    interaction_history: List[Dict[str, Any]]
    last_updated: datetime


class ContextualIntelligence:
    """
    Advanced contextual intelligence system for Agent Zero
    """
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.conversation_patterns: Dict[str, ConversationPattern] = {}
        self.user_profiles: Dict[str, UserProfile] = {}
        self.semantic_cache: Dict[str, Any] = {}
        self.intent_history: List[IntentAnalysis] = []
        self.prediction_accuracy: Dict[str, float] = defaultdict(float)
        
    async def analyze_intent(self, message: str, conversation_history: str = "") -> IntentAnalysis:
        """
        Perform comprehensive intent analysis on user message
        """
        
        # Create analysis prompt
        analysis_prompt = f"""
        Perform advanced contextual analysis of this user message:
        
        MESSAGE: {message}
        
        CONVERSATION HISTORY: {conversation_history[-2000:] if conversation_history else "None"}
        
        Analyze and provide JSON response:
        {{
            "primary_intent": "question|task|command|exploration|problem_solving|creative|analysis|learning|automation|collaboration",
            "secondary_intents": ["array of secondary intents"],
            "confidence": 0.0-1.0,
            "complexity": 1-5,
            "emotional_tone": "neutral|positive|negative|urgent|frustrated|excited|confused|confident",
            "entities": [
                {{
                    "text": "entity text",
                    "type": "person|organization|technology|concept|file|url|date|number",
                    "confidence": 0.0-1.0
                }}
            ],
            "keywords": ["key", "terms", "extracted"],
            "context_requirements": ["what context is needed"],
            "predicted_followup": "likely next user action or question",
            "reasoning": "detailed analysis reasoning"
        }}
        """
        
        try:
            analysis_result = await self.agent.call_utility_model(
                system="You are an advanced contextual intelligence analyzer. Provide deep semantic analysis.",
                message=analysis_prompt,
                background=True
            )
            
            analysis_data = dirty_json.try_parse(analysis_result)
            
            if not analysis_data:
                return self._create_fallback_analysis(message)
            
            # Convert to structured analysis
            intent_analysis = IntentAnalysis(
                primary_intent=IntentType(analysis_data.get("primary_intent", "question")),
                secondary_intents=[IntentType(i) for i in analysis_data.get("secondary_intents", [])],
                confidence=float(analysis_data.get("confidence", 0.7)),
                complexity=ContextualComplexity(int(analysis_data.get("complexity", 2))),
                emotional_tone=EmotionalTone(analysis_data.get("emotional_tone", "neutral")),
                entities=[
                    SemanticEntity(
                        text=e.get("text", ""),
                        entity_type=e.get("type", "unknown"),
                        confidence=float(e.get("confidence", 0.5)),
                        start_pos=0,
                        end_pos=len(e.get("text", ""))
                    ) for e in analysis_data.get("entities", [])
                ],
                keywords=analysis_data.get("keywords", []),
                context_requirements=analysis_data.get("context_requirements", []),
                predicted_followup=analysis_data.get("predicted_followup")
            )
            
            # Store in history
            self.intent_history.append(intent_analysis)
            
            # Update semantic cache
            self.semantic_cache[message] = intent_analysis
            
            return intent_analysis
            
        except Exception as e:
            PrintStyle().error(f"Intent analysis failed: {str(e)}")
            return self._create_fallback_analysis(message)
    
    async def predict_user_needs(self, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict user needs based on current context and history
        """
        
        prediction_prompt = f"""
        Based on the current context and conversation patterns, predict user needs:
        
        CURRENT CONTEXT: {json.dumps(current_context, indent=2)}
        
        RECENT INTENT HISTORY: {json.dumps([
            {
                "intent": analysis.primary_intent.value,
                "complexity": analysis.complexity.value,
                "tone": analysis.emotional_tone.value,
                "keywords": analysis.keywords[:5]
            } for analysis in self.intent_history[-5:]
        ], indent=2)}
        
        Provide predictions in JSON format:
        {{
            "immediate_needs": ["what user likely needs right now"],
            "upcoming_tasks": ["tasks user might want to do next"],
            "potential_blockers": ["what might prevent user from succeeding"],
            "suggested_actions": ["proactive suggestions"],
            "resource_requirements": ["tools/info user might need"],
            "confidence_score": 0.0-1.0,
            "reasoning": "explanation of predictions"
        }}
        """
        
        try:
            prediction_result = await self.agent.call_utility_model(
                system="You are a predictive intelligence system. Anticipate user needs accurately.",
                message=prediction_prompt,
                background=True
            )
            
            predictions = dirty_json.try_parse(prediction_result)
            
            if predictions:
                # Store prediction for accuracy tracking
                prediction_id = f"pred_{datetime.now().timestamp()}"
                self.prediction_accuracy[prediction_id] = 0.0  # Will be updated when validated
                
                return {
                    "prediction_id": prediction_id,
                    **predictions
                }
            
        except Exception as e:
            PrintStyle().error(f"Prediction failed: {str(e)}")
        
        return {
            "immediate_needs": [],
            "upcoming_tasks": [],
            "potential_blockers": [],
            "suggested_actions": [],
            "resource_requirements": [],
            "confidence_score": 0.0,
            "reasoning": "Prediction system unavailable"
        }
    
    async def analyze_conversation_patterns(self) -> Dict[str, ConversationPattern]:
        """
        Analyze conversation patterns to identify trends
        """
        
        if len(self.intent_history) < 3:
            return {}
        
        patterns = {}
        
        # Analyze intent sequences
        intent_sequences = []
        for i in range(len(self.intent_history) - 1):
            current = self.intent_history[i].primary_intent.value
            next_intent = self.intent_history[i + 1].primary_intent.value
            intent_sequences.append(f"{current}->{next_intent}")
        
        # Count pattern frequencies
        pattern_counts = Counter(intent_sequences)
        
        for pattern, frequency in pattern_counts.items():
            if frequency >= 2:  # Only patterns that occur multiple times
                patterns[pattern] = ConversationPattern(
                    pattern_type=pattern,
                    frequency=frequency,
                    last_occurrence=datetime.now(timezone.utc),
                    success_rate=0.8,  # Will be calculated based on actual outcomes
                    typical_duration=120.0,  # Will be calculated from timing data
                    common_followups=[]
                )
        
        self.conversation_patterns.update(patterns)
        return patterns
    
    async def extract_semantic_entities(self, text: str) -> List[SemanticEntity]:
        """
        Extract semantic entities from text using advanced NLP
        """
        
        entities = []
        
        # Technology entities
        tech_patterns = {
            "programming_language": r"\b(Python|JavaScript|Java|C\+\+|Go|Rust|TypeScript|PHP|Ruby|Swift|Kotlin)\b",
            "framework": r"\b(React|Vue|Angular|Django|Flask|Express|Spring|Laravel|Rails)\b",
            "database": r"\b(MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|Cassandra)\b",
            "cloud_service": r"\b(AWS|Azure|GCP|Docker|Kubernetes|Terraform)\b",
            "tool": r"\b(Git|GitHub|GitLab|Jenkins|Jira|Slack|Discord)\b"
        }
        
        for entity_type, pattern in tech_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(SemanticEntity(
                    text=match.group(),
                    entity_type=entity_type,
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end()
                ))
        
        # File paths
        file_pattern = r"[/\\]?(?:[a-zA-Z0-9_-]+[/\\])*[a-zA-Z0-9_-]+\.[a-zA-Z0-9]+"
        file_matches = re.finditer(file_pattern, text)
        for match in file_matches:
            entities.append(SemanticEntity(
                text=match.group(),
                entity_type="file_path",
                confidence=0.8,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        # URLs
        url_pattern = r"https?://[^\s]+"
        url_matches = re.finditer(url_pattern, text)
        for match in url_matches:
            entities.append(SemanticEntity(
                text=match.group(),
                entity_type="url",
                confidence=0.95,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        # Numbers and quantities
        number_pattern = r"\b\d+(?:\.\d+)?(?:\s*(?:MB|GB|TB|KB|ms|seconds?|minutes?|hours?|days?|%))?\b"
        number_matches = re.finditer(number_pattern, text)
        for match in number_matches:
            entities.append(SemanticEntity(
                text=match.group(),
                entity_type="quantity",
                confidence=0.7,
                start_pos=match.start(),
                end_pos=match.end()
            ))
        
        return entities
    
    async def build_user_profile(self, user_id: str = "default") -> UserProfile:
        """
        Build dynamic user profile based on interaction history
        """
        
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
        else:
            profile = UserProfile(
                user_id=user_id,
                preferences={},
                expertise_areas=[],
                communication_style="direct",
                typical_tasks=[],
                learning_patterns={},
                interaction_history=[],
                last_updated=datetime.now(timezone.utc)
            )
        
        # Analyze recent interactions to update profile
        if self.intent_history:
            # Extract expertise areas from entities
            tech_entities = []
            for analysis in self.intent_history[-20:]:  # Last 20 interactions
                tech_entities.extend([
                    entity.text for entity in analysis.entities 
                    if entity.entity_type in ["programming_language", "framework", "database", "tool"]
                ])
            
            # Update expertise areas
            tech_counter = Counter(tech_entities)
            profile.expertise_areas = [tech for tech, count in tech_counter.most_common(10)]
            
            # Analyze communication style
            complexity_scores = [analysis.complexity.value for analysis in self.intent_history[-10:]]
            avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 2
            
            if avg_complexity >= 4:
                profile.communication_style = "expert"
            elif avg_complexity >= 3:
                profile.communication_style = "technical"
            elif avg_complexity >= 2:
                profile.communication_style = "moderate"
            else:
                profile.communication_style = "beginner"
            
            # Extract typical tasks
            task_intents = [
                analysis.primary_intent.value for analysis in self.intent_history[-15:]
                if analysis.primary_intent in [IntentType.TASK, IntentType.PROBLEM_SOLVING, IntentType.AUTOMATION]
            ]
            task_counter = Counter(task_intents)
            profile.typical_tasks = [task for task, count in task_counter.most_common(5)]
        
        profile.last_updated = datetime.now(timezone.utc)
        self.user_profiles[user_id] = profile
        
        return profile
    
    async def generate_contextual_suggestions(
        self, 
        current_message: str,
        intent_analysis: IntentAnalysis
    ) -> List[Dict[str, Any]]:
        """
        Generate contextual suggestions based on analysis
        """
        
        suggestions = []
        
        # Intent-based suggestions
        if intent_analysis.primary_intent == IntentType.PROBLEM_SOLVING:
            suggestions.extend([
                {
                    "type": "tool_suggestion",
                    "title": "Use Code Execution",
                    "description": "Execute code to test solutions",
                    "action": "code_execution_tool",
                    "priority": 8
                },
                {
                    "type": "workflow_suggestion", 
                    "title": "Break Down Problem",
                    "description": "Use subordinate agents for complex analysis",
                    "action": "call_subordinate",
                    "priority": 7
                }
            ])
        
        elif intent_analysis.primary_intent == IntentType.ANALYSIS:
            suggestions.extend([
                {
                    "type": "tool_suggestion",
                    "title": "Search for Data",
                    "description": "Use search engine for additional information",
                    "action": "search_engine",
                    "priority": 8
                },
                {
                    "type": "memory_suggestion",
                    "title": "Check Previous Analysis",
                    "description": "Search memory for related analysis",
                    "action": "memory_load",
                    "priority": 6
                }
            ])
        
        elif intent_analysis.primary_intent == IntentType.CREATIVE:
            suggestions.extend([
                {
                    "type": "collaboration_suggestion",
                    "title": "Creative Team",
                    "description": "Orchestrate creative and analyst agents",
                    "action": "orchestrate_agents",
                    "priority": 9
                }
            ])
        
        # Complexity-based suggestions
        if intent_analysis.complexity.value >= 4:
            suggestions.append({
                "type": "orchestration_suggestion",
                "title": "Multi-Agent Approach",
                "description": "Use specialized agents for expert-level task",
                "action": "orchestrate_agents",
                "priority": 9
            })
        
        # Entity-based suggestions
        for entity in intent_analysis.entities:
            if entity.entity_type == "file_path":
                suggestions.append({
                    "type": "file_suggestion",
                    "title": f"Analyze {entity.text}",
                    "description": "Use document query tool for file analysis",
                    "action": "document_query",
                    "priority": 7
                })
            elif entity.entity_type == "url":
                suggestions.append({
                    "type": "web_suggestion",
                    "title": f"Analyze Website",
                    "description": "Use browser agent for web interaction",
                    "action": "browser_agent",
                    "priority": 6
                })
        
        # Sort by priority
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    async def learn_from_interaction(
        self, 
        user_message: str,
        agent_response: str,
        user_feedback: Optional[str] = None,
        success_indicators: Optional[Dict[str, Any]] = None
    ):
        """
        Learn from user interactions to improve future predictions
        """
        
        # Analyze the interaction
        intent_analysis = await self.analyze_intent(user_message)
        
        # Extract learning signals
        learning_data = {
            "timestamp": datetime.now(timezone.utc),
            "user_message": user_message,
            "intent": intent_analysis.primary_intent.value,
            "complexity": intent_analysis.complexity.value,
            "emotional_tone": intent_analysis.emotional_tone.value,
            "agent_response_length": len(agent_response),
            "entities_found": len(intent_analysis.entities),
            "success_score": self._calculate_success_score(
                user_feedback, success_indicators
            )
        }
        
        # Update user profile
        user_profile = await self.build_user_profile()
        user_profile.interaction_history.append(learning_data)
        
        # Keep only recent history (last 100 interactions)
        if len(user_profile.interaction_history) > 100:
            user_profile.interaction_history = user_profile.interaction_history[-100:]
        
        # Update learning patterns
        intent_key = intent_analysis.primary_intent.value
        if intent_key in user_profile.learning_patterns:
            # Exponential moving average
            alpha = 0.1
            user_profile.learning_patterns[intent_key] = (
                alpha * learning_data["success_score"] + 
                (1 - alpha) * user_profile.learning_patterns[intent_key]
            )
        else:
            user_profile.learning_patterns[intent_key] = learning_data["success_score"]
        
        # Store learning in memory
        db = await Memory.get(self.agent)
        await db.insert_text(
            f"Interaction Learning: {intent_analysis.primary_intent.value} - Success: {learning_data['success_score']:.2f}",
            {
                "area": Memory.Area.MAIN.value,
                "type": "contextual_learning",
                "intent": intent_analysis.primary_intent.value,
                "success_score": learning_data["success_score"],
                "timestamp": learning_data["timestamp"].isoformat()
            }
        )
    
    async def get_contextual_recommendations(
        self, 
        current_message: str,
        conversation_history: str = ""
    ) -> Dict[str, Any]:
        """
        Get comprehensive contextual recommendations
        """
        
        # Perform intent analysis
        intent_analysis = await self.analyze_intent(current_message, conversation_history)
        
        # Generate suggestions
        suggestions = await self.generate_contextual_suggestions(current_message, intent_analysis)
        
        # Predict user needs
        current_context = {
            "message": current_message,
            "intent": intent_analysis.primary_intent.value,
            "complexity": intent_analysis.complexity.value,
            "entities": [e.text for e in intent_analysis.entities]
        }
        predictions = await self.predict_user_needs(current_context)
        
        # Analyze patterns
        patterns = await self.analyze_conversation_patterns()
        
        # Build user profile
        user_profile = await self.build_user_profile()
        
        return {
            "intent_analysis": {
                "primary_intent": intent_analysis.primary_intent.value,
                "confidence": intent_analysis.confidence,
                "complexity": intent_analysis.complexity.value,
                "emotional_tone": intent_analysis.emotional_tone.value,
                "entities": [
                    {
                        "text": e.text,
                        "type": e.entity_type,
                        "confidence": e.confidence
                    } for e in intent_analysis.entities
                ],
                "keywords": intent_analysis.keywords,
                "predicted_followup": intent_analysis.predicted_followup
            },
            "suggestions": suggestions,
            "predictions": predictions,
            "conversation_patterns": {
                pattern_type: {
                    "frequency": pattern.frequency,
                    "success_rate": pattern.success_rate
                } for pattern_type, pattern in patterns.items()
            },
            "user_profile": {
                "communication_style": user_profile.communication_style,
                "expertise_areas": user_profile.expertise_areas[:5],
                "typical_tasks": user_profile.typical_tasks[:3]
            }
        }
    
    def _create_fallback_analysis(self, message: str) -> IntentAnalysis:
        """Create fallback analysis when AI analysis fails"""
        
        # Simple heuristic analysis
        message_lower = message.lower()
        
        # Determine intent based on keywords
        if any(word in message_lower for word in ["what", "how", "why", "when", "where", "?"]):
            primary_intent = IntentType.QUESTION
        elif any(word in message_lower for word in ["create", "build", "make", "develop", "implement"]):
            primary_intent = IntentType.TASK
        elif any(word in message_lower for word in ["analyze", "examine", "study", "investigate"]):
            primary_intent = IntentType.ANALYSIS
        else:
            primary_intent = IntentType.EXPLORATION
        
        # Determine complexity based on length and technical terms
        tech_terms = len(re.findall(r"\b(?:API|database|server|algorithm|framework|architecture)\b", message_lower))
        complexity = ContextualComplexity.SIMPLE
        if len(message) > 200 or tech_terms > 3:
            complexity = ContextualComplexity.COMPLEX
        elif len(message) > 100 or tech_terms > 1:
            complexity = ContextualComplexity.MODERATE
        
        return IntentAnalysis(
            primary_intent=primary_intent,
            secondary_intents=[],
            confidence=0.6,
            complexity=complexity,
            emotional_tone=EmotionalTone.NEUTRAL,
            entities=[],
            keywords=message.split()[:10],
            context_requirements=[]
        )
    
    def _calculate_success_score(
        self, 
        user_feedback: Optional[str],
        success_indicators: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate success score for interaction"""
        
        score = 0.5  # Default neutral score
        
        if user_feedback:
            feedback_lower = user_feedback.lower()
            if any(word in feedback_lower for word in ["good", "great", "perfect", "excellent", "thanks"]):
                score += 0.3
            elif any(word in feedback_lower for word in ["bad", "wrong", "error", "failed", "terrible"]):
                score -= 0.3
        
        if success_indicators:
            if success_indicators.get("task_completed", False):
                score += 0.2
            if success_indicators.get("user_satisfied", False):
                score += 0.2
            if success_indicators.get("error_occurred", False):
                score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    async def save_intelligence_state(self):
        """Save contextual intelligence state"""
        
        state = {
            "conversation_patterns": {
                pattern_type: {
                    "pattern_type": pattern.pattern_type,
                    "frequency": pattern.frequency,
                    "last_occurrence": pattern.last_occurrence.isoformat(),
                    "success_rate": pattern.success_rate,
                    "typical_duration": pattern.typical_duration,
                    "common_followups": pattern.common_followups
                } for pattern_type, pattern in self.conversation_patterns.items()
            },
            "user_profiles": {
                user_id: {
                    "user_id": profile.user_id,
                    "preferences": profile.preferences,
                    "expertise_areas": profile.expertise_areas,
                    "communication_style": profile.communication_style,
                    "typical_tasks": profile.typical_tasks,
                    "learning_patterns": profile.learning_patterns,
                    "last_updated": profile.last_updated.isoformat()
                } for user_id, profile in self.user_profiles.items()
            },
            "prediction_accuracy": dict(self.prediction_accuracy),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Save to memory
        db = await Memory.get(self.agent)
        await db.insert_text(
            f"Contextual Intelligence State: {len(self.conversation_patterns)} patterns, {len(self.user_profiles)} profiles",
            {
                "area": Memory.Area.MAIN.value,
                "type": "contextual_intelligence_state",
                "state_data": json.dumps(state),
                "timestamp": state["timestamp"]
            }
        )


# Global intelligence instance
_global_intelligence: Optional[ContextualIntelligence] = None


def get_contextual_intelligence(agent: Agent) -> ContextualIntelligence:
    """Get or create global contextual intelligence instance"""
    global _global_intelligence
    
    if _global_intelligence is None:
        _global_intelligence = ContextualIntelligence(agent)
    
    return _global_intelligence


def reset_contextual_intelligence():
    """Reset global intelligence (for testing/cleanup)"""
    global _global_intelligence
    _global_intelligence = None