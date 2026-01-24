"""
Natural Language Processing Parser for Todo App MCP Server

This module implements a rule-based natural language processing system that
combines pattern matching with intent classification to interpret todo commands.
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
from ..models.parsed_command import ParsedCommand, IntentType
from ..models.todo_reference import TodoReference, IdentifierType


class LanguageCode(Enum):
    ENGLISH = "en"
    URDU = "ur"
    HINDI = "hi"
    MIXED = "mixed"


class NLPParser:
    """
    Natural Language Processing Parser for Todo commands
    """

    def __init__(self):
        # Intent patterns for different operations
        self.intent_patterns = {
            IntentType.ADD_TODO: [
                r'add\s+(a\s+|new\s+|another\s+)?(todo|task|item)\s+(to|for|about)\s+(.+)',
                r'create\s+(a\s+|new\s+|another\s+)?(todo|task|item)\s+(to|for|about)\s+(.+)',
                r'make\s+(a\s+|new\s+)?(todo|task|item)\s+(to|for|about)\s+(.+)',
                r'add\s+(.+)',  # Simple add pattern
                r'need\s+to\s+(.+)',  # "I need to buy groceries"
                r'want\s+to\s+(.+)',  # "I want to complete the report"
            ],
            IntentType.DELETE_TODO: [
                r'(delete|remove|del)\s+(the\s+|my\s+|a\s+)?(.+?)\s+(task|todo|item)',
                r'(delete|remove|del)\s+(.+)',  # Simple delete pattern
                r'delete\s+(the\s+)?(.+)',  # Another delete pattern
                r'get\s+rid\s+of\s+(.+)',  # "get rid of my meeting task"
                r'cancel\s+(.+)',  # "cancel my appointment task"
            ],
            IntentType.UPDATE_TODO: [
                r'(update|change|modify|edit)\s+(the\s+|my\s+|a\s+)?(.+?)\s+(task|todo|item)',
                r'(update|change|modify|edit)\s+(.+)',  # Simple update pattern
                r'change\s+(.+)',  # "change my task"
                r'modify\s+(.+)',  # "modify my task"
            ],
            IntentType.COMPLETE_TODO: [
                r'(complete|finish|done|mark.*as.*complete|mark.*as.*done)\s+(the\s+|my\s+|a\s+)?(.+?)\s+(task|todo|item)',
                r'(complete|finish|done|mark.*as.*complete|mark.*as.*done)\s+(.+)',  # Simple complete pattern
                r'mark\s+(the\s+|my\s+|a\s+)?(.+?)\s+(as\s+)?(complete|done)',  # "mark my task as done"
                r'finish\s+(.+)',  # "finish my task"
            ],
            IntentType.LIST_TODOS: [
                r'(show|list|display|view|see)\s+(my\s+|all\s+|the\s+)?(tasks|todos|items|todo\s+list)',
                r'what.*tasks',  # "what tasks do I have?"
                r'what.*todo',   # "what todo items do I have?"
                r'give.*me.*list',  # "give me a list of my tasks"
                r'list.*all',  # "list all my tasks"
            ]
        }

        # Multilingual patterns (English-Urdu/Hindi mixed expressions)
        self.multilingual_patterns = {
            "ya": ["or", "either"],  # "ya" means "or" in Urdu/Hindi
            "them": ["then", "and"],  # "them" can be used as "then" in mixed expressions
            "jis mai": ["in which", "where", "that"],  # "jis mai" means "in which" in Urdu
        }

        # Context reference patterns
        self.context_patterns = {
            "that one": ["that", "that task", "that item"],
            "the last one": ["last task", "recent task", "previous task"],
            "previous": ["previous task", "earlier task"],
            "first one": ["first task", "initial task"],
        }

    def detect_language(self, text: str) -> LanguageCode:
        """
        Detect the language of the input text (basic implementation)
        """
        text_lower = text.lower()

        # Simple heuristic for detecting multilingual content
        mixed_indicators = ['ya', 'jis', 'mai', 'ke', 'ka', 'ki']
        if any(indicator in text_lower for indicator in mixed_indicators):
            return LanguageCode.MIXED

        # More sophisticated language detection would go here
        return LanguageCode.ENGLISH

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess the input text by normalizing and handling multilingual expressions
        """
        text = text.strip()

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Handle common multilingual expressions
        for key, replacements in self.multilingual_patterns.items():
            for replacement in replacements:
                # Replace in a case-insensitive manner
                text = re.sub(r'\b' + re.escape(key) + r'\b', replacement, text, flags=re.IGNORECASE)

        return text

    def identify_intent(self, text: str) -> Tuple[Optional[IntentType], float]:
        """
        Identify the intent from the input text with confidence score

        Args:
            text: Input text to analyze

        Returns:
            Tuple of (intent_type, confidence_score)
        """
        processed_text = self.preprocess_text(text).lower()

        best_match = (None, 0.0)  # (intent, confidence)

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, processed_text)
                if match:
                    # Calculate confidence based on pattern specificity and match quality
                    # For now, assign a high confidence for matches
                    confidence = 0.9

                    # Adjust confidence based on pattern complexity
                    if len(match.groups()) > 1:
                        confidence = 0.95  # More specific match
                    else:
                        confidence = 0.85  # Less specific match

                    # Keep the highest confidence match
                    if confidence > best_match[1]:
                        best_match = (intent, confidence)

        return best_match

    def extract_entities(self, text: str, intent: IntentType) -> List[Dict[str, str]]:
        """
        Extract entities from the text based on the identified intent
        """
        entities = []
        processed_text = self.preprocess_text(text).lower()

        # Select appropriate pattern based on intent
        patterns = self.intent_patterns.get(intent, [])

        for pattern in patterns:
            match = re.search(pattern, processed_text)
            if match:
                groups = match.groups()

                # Extract different types of entities based on intent
                if intent == IntentType.ADD_TODO:
                    # Extract the task description from the last capturing group
                    if len(groups) >= 1:
                        desc = groups[-1].strip()
                        if desc:
                            entities.append({"type": "task_description", "value": desc})

                elif intent == IntentType.DELETE_TODO:
                    # Extract the task identifier
                    if len(groups) >= 1:
                        identifier = groups[-1].strip()
                        if identifier:
                            entities.append({"type": "task_identifier", "value": identifier})

                elif intent == IntentType.UPDATE_TODO:
                    # Extract the task identifier and potentially new content
                    if len(groups) >= 1:
                        identifier = groups[-1].strip()
                        if identifier:
                            entities.append({"type": "task_identifier", "value": identifier})

                elif intent == IntentType.COMPLETE_TODO:
                    # Extract the task identifier
                    if len(groups) >= 1:
                        identifier = groups[-1].strip()
                        if identifier:
                            entities.append({"type": "task_identifier", "value": identifier})

                elif intent == IntentType.LIST_TODOS:
                    # Extract list filters
                    if "pending" in processed_text or "incomplete" in processed_text:
                        entities.append({"type": "filter_status", "value": "Pending"})
                    elif "completed" in processed_text or "done" in processed_text:
                        entities.append({"type": "filter_status", "value": "Completed"})

                # Break after first match since we found our entities
                break

        return entities

    def parse_context_reference(self, text: str) -> Optional[TodoReference]:
        """
        Parse context-sensitive references like "that one", "the last one", etc.
        """
        text_lower = text.lower().strip()

        for context_term, alternatives in self.context_patterns.items():
            if context_term in text_lower:
                return TodoReference(
                    identifier_type=IdentifierType.CONTEXT_REFERENCE,
                    value=context_term,
                    confidence=0.9
                )

            for alt in alternatives:
                if alt in text_lower:
                    return TodoReference(
                        identifier_type=IdentifierType.CONTEXT_REFERENCE,
                        value=alt,
                        confidence=0.8
                    )

        # Check if the text might be referring to a position
        position_patterns = [
            (r'first', 1),
            (r'second', 2),
            (r'third', 3),
            (r'(\d+)\s*(st|nd|rd|th)', lambda m: int(m.group(1)) if m.group(1).isdigit() else None)
        ]

        for pattern, pos_val in position_patterns[:-1]:  # Handle simple patterns
            if re.search(pattern, text_lower):
                return TodoReference(
                    identifier_type=IdentifierType.POSITION,
                    value=str(pos_val) if isinstance(pos_val, int) else "1",  # Default to first
                    confidence=0.7
                )

        # Handle numbered positions
        num_match = re.search(r'(\d+)\s*(st|nd|rd|th)', text_lower)
        if num_match and num_match.group(1).isdigit():
            return TodoReference(
                identifier_type=IdentifierType.POSITION,
                value=num_match.group(1),
                confidence=0.7
            )

        return None

    def parse_command(self, raw_input: str) -> ParsedCommand:
        """
        Parse a natural language command into a structured format

        Args:
            raw_input: The original user input

        Returns:
            ParsedCommand object with intent, entities, and confidence
        """
        # Detect language
        language_code = self.detect_language(raw_input)

        # Identify intent
        intent, confidence = self.identify_intent(raw_input)

        # Extract entities
        entities = []
        if intent:
            entities = self.extract_entities(raw_input, intent)

        # Check for context references
        context_ref = self.parse_context_reference(raw_input)

        # Create the parsed command
        parsed_cmd = ParsedCommand(
            intent=intent,
            entities=entities,
            confidence=confidence,
            resolved_action=self._determine_resolved_action(intent, entities),
            raw_input=raw_input,
            language_code=language_code.value,
            context_reference=context_ref
        )

        return parsed_cmd

    def _determine_resolved_action(self, intent: Optional[IntentType], entities: List[Dict]) -> str:
        """
        Determine the resolved action based on intent and entities
        """
        if not intent:
            return "UNKNOWN"

        action_map = {
            IntentType.ADD_TODO: "ADD_TASK",
            IntentType.DELETE_TODO: "DELETE_TASK",
            IntentType.UPDATE_TODO: "UPDATE_TASK",
            IntentType.COMPLETE_TODO: "MARK_COMPLETE",
            IntentType.LIST_TODOS: "LIST_TASKS"
        }

        return action_map.get(intent, "UNKNOWN")


# Global instance for convenience
nlp_parser = NLPParser()