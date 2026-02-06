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
        Enhanced to handle more multilingual patterns
        """
        text = text.strip()

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Enhanced multilingual patterns mapping
        enhanced_multilingual_patterns = {
            "ya": ["or", "and"],  # "ya" can mean "or" or "and" in Urdu/Hindi
            "them": ["then", "and", "to them", "to"],  # "them" used as "then" in mixed expressions
            "jis mai": ["in which", "where", "that"],  # "jis mai" means "in which" in Urdu
            "jis": ["which", "that", "the one which"],  # "jis" means "which" in Urdu
            "mai": ["in", "at", "me"],  # "mai" means "in" in Urdu
            "ke": ["of", "to", "for", "and"],  # "ke" is possessive or connector in Urdu
            "ka": ["of", "the"],  # "ka" is possessive in Urdu/Hindi
            "aur": ["and", "also"],  # "aur" means "and" in Urdu/Hindi
            "karna": ["to do", "to make", "to perform"],  # "karna" means "to do" in Hindi/Urdu
            "kar": ["do", "make", "perform"],  # "kar" is "do" in Hindi/Urdu
            "liye": ["for", "to"],  # "liye" means "for" in Urdu/Hindi
            "ko": ["to", "for", "him", "her"],  # "ko" is object marker in Hindi/Urdu
            "hai": ["is", "are", "am"],  # "hai" means "is/are/am" in Hindi/Urdu
            "hain": ["are", "is"],  # "hain" is plural of "hai" in Hindi/Urdu
            "thaa": ["was", "were"],  # past tense in Hindi/Urdu
            "tha": ["was", "were"],  # past tense in Hindi/Urdu
            "naam": ["name", "title"],  # "naam" means "name" in Hindi/Urdu
            "kaam": ["work", "task", "job"],  # "kaam" means "work/task" in Hindi/Urdu
            "kam": ["work", "task", "job"],  # alternate spelling of "kaam"
            "tassveer": ["picture", "image", "photo"],  # "tassveer" means "picture" in Urdu
            "chahiye": ["need", "want", "should"],  # "chahiye" means "need/want" in Hindi/Urdu
            "chahiyega": ["will need", "will want"],  # future form of "chahiye"
        }

        # Handle common multilingual expressions
        for key, replacements in enhanced_multilingual_patterns.items():
            for replacement in replacements:
                # Replace in a case-insensitive manner, matching whole words
                text = re.sub(r'\b' + re.escape(key) + r'\b', replacement, text, flags=re.IGNORECASE)

        return text

    def identify_intent(self, text: str) -> Tuple[Optional[IntentType], float]:
        """
        Identify the intent from the input text with confidence score
        Enhanced to handle complex multilingual patterns first, before preprocessing

        Args:
            text: Input text to analyze

        Returns:
            Tuple of (intent_type, confidence_score)
        """
        original_text = text.lower()

        # First, check for complex multilingual patterns that need to be handled specially
        # We do this on the original text before preprocessing to avoid text transformation issues
        complex_patterns = [
            # Pattern for: "add new task name <title> and description them <description>"
            (r'add\s+new\s+task\s+name\s+(.+?)\s+and\s+description\s+them\s+(.+)', IntentType.ADD_TODO),
            # Pattern for: "create new task name <title> and description them <description>"
            (r'create\s+new\s+task\s+name\s+(.+?)\s+and\s+description\s+them\s+(.+)', IntentType.ADD_TODO),
            # Pattern for: "create task name <title> and description them <description>"
            (r'create\s+task\s+name\s+(.+?)\s+and\s+description\s+them\s+(.+)', IntentType.ADD_TODO),
            # Pattern for: "add task name <title> and description them <description>"
            (r'add\s+task\s+name\s+(.+?)\s+and\s+description\s+them\s+(.+)', IntentType.ADD_TODO),
            # Pattern for: "add task name <title> description them <description>"
            (r'add\s+task\s+name\s+(.+?)\s+description\s+them\s+(.+)', IntentType.ADD_TODO),
            # Pattern for: "add new task title <title> and description them <description>"
            (r'add\s+new\s+task\s+title\s+(.+?)\s+and\s+description\s+them\s+(.+)', IntentType.ADD_TODO),
            # Pattern for: "add task title <title> and description them <description>"
            (r'add\s+task\s+title\s+(.+?)\s+and\s+description\s+them\s+(.+)', IntentType.ADD_TODO),
            # Pattern for: "add task title <title> description them <description>"
            (r'add\s+task\s+title\s+(.+?)\s+description\s+them\s+(.+)', IntentType.ADD_TODO),
        ]

        for pattern, intent in complex_patterns:
            match = re.search(pattern, original_text)
            if match:
                # High confidence for these specific complex patterns
                return (intent, 0.98)

        # If no complex patterns match, preprocess the text and use standard patterns
        processed_text = self.preprocess_text(text).lower()

        best_match = (None, 0.0)  # (intent, confidence)

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, processed_text)
                if match:
                    # Calculate confidence based on pattern specificity and match quality
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
        Enhanced to handle complex patterns like "add new task name task 01 and description them new task"
        """
        entities = []

        # First, try to handle complex multilingual patterns specifically
        # Do this on the original text before preprocessing to avoid transformation issues
        original_text = text.lower()

        if intent == IntentType.ADD_TODO:
            # Look for patterns like "add new task name <title> and description them <description>"
            complex_patterns = [
                # Pattern for: "add new task name task 01 and description them new task"
                r'add\s+new\s+task\s+name\s+(.+?)\s+and\s+description\s+them\s+(.+)',
                # Pattern for: "create new task name buy groceries and description them go to market"
                r'create\s+new\s+task\s+name\s+(.+?)\s+and\s+description\s+them\s+(.+)',
                # Pattern for: "create task name buy groceries and description them go to market"
                r'create\s+task\s+name\s+(.+?)\s+and\s+description\s+them\s+(.+)',
                # Pattern for: "add task name groceries and description them buy milk and bread"
                r'add\s+task\s+name\s+(.+?)\s+and\s+description\s+them\s+(.+)',
                # Pattern for: "add task name task 01 description them new task"
                r'add\s+task\s+name\s+(.+?)\s+description\s+them\s+(.+)',
                # Pattern for: "add new task title task 01 and description them new task"
                r'add\s+new\s+task\s+title\s+(.+?)\s+and\s+description\s+them\s+(.+)',
                # Pattern for: "add task title task 01 and description them new task"
                r'add\s+task\s+title\s+(.+?)\s+and\s+description\s+them\s+(.+)',
                # Pattern for: "add task title task 01 description them new task"
                r'add\s+task\s+title\s+(.+?)\s+description\s+them\s+(.+)',
                # More general pattern for "name" and "description"
                r'(?:add|create|make)\s+(?:new\s+)?(?:task|todo|item)\s+(?:name|title)\s+(.+?)\s+(?:and\s+description|description)\s+(?:them|is|to|as)?\s+(.+)',
            ]

            for pattern in complex_patterns:
                match = re.search(pattern, original_text)
                if match:
                    title = match.group(1).strip()
                    description = match.group(2).strip()

                    # Add both title and description as separate entities
                    entities.append({"type": "task_title", "value": title})
                    entities.append({"type": "task_description", "value": description})
                    return entities

        # If complex patterns didn't match, use the original approach
        # Process the text and use standard patterns
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