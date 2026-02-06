"""
Command Processor for Todo App MCP Server

This module processes parsed commands and orchestrates the execution of todo operations.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.parsed_command import ParsedCommand, IntentType
from ..models.todo_operation import TodoOperation, OperationType
from ..models.todo_reference import TodoReference, IdentifierType
from ..models.nlp_command import NaturalLanguageCommand
from .todo_operations import TodoOperationsService
from .nlp_parser import nlp_parser


class CommandProcessor:
    """
    Command Processor that takes parsed commands and executes todo operations
    """

    def __init__(self, db_session: Session, user_id: str):
        self.db_session = db_session
        self.user_id = user_id
        self.todo_ops_service = TodoOperationsService(db_session, user_id)

    def process_command(self, nlp_command: NaturalLanguageCommand) -> Dict[str, Any]:
        """
        Process a natural language command and return the result

        Args:
            nlp_command: The natural language command to process

        Returns:
            Dictionary containing the result of the command processing
        """
        try:
            # Parse the command using the NLP parser
            parsed_command = nlp_parser.parse_command(nlp_command.raw_input)

            # Validate the parsed command
            validation_result = self.validate_parsed_command(parsed_command)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'operation_performed': 'VALIDATION_ERROR',
                    'message': validation_result['error'],
                    'parsed_command': parsed_command.to_dict(),
                    'suggestions': validation_result.get('suggestions', [])
                }

            # Execute the appropriate operation based on intent
            result = self.execute_operation(parsed_command)

            # Format the response
            return self.format_response(result, parsed_command)

        except Exception as e:
            return {
                'success': False,
                'operation_performed': 'EXCEPTION',
                'message': f'Error processing command: {str(e)}',
                'suggestions': ['Please try rephrasing your command', 'Check your command syntax']
            }

    def validate_parsed_command(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """
        Validate the parsed command before execution
        """
        if not parsed_command.intent:
            return {
                'valid': False,
                'error': 'Could not understand the command intent. Please try rephrasing.',
                'suggestions': ['Try using clear keywords like "add", "delete", "complete"', 'Be more specific about what you want to do']
            }

        if parsed_command.confidence < 0.7:
            return {
                'valid': False,
                'error': 'Command confidence is low. The system is uncertain about what you want to do.',
                'suggestions': ['Be more specific in your command', 'Use clearer language']
            }

        return {'valid': True}

    def execute_operation(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """
        Execute the appropriate operation based on the parsed command intent
        """
        intent = parsed_command.intent

        if intent == IntentType.ADD_TODO:
            return self.handle_add_todo(parsed_command)
        elif intent == IntentType.DELETE_TODO:
            return self.handle_delete_todo(parsed_command)
        elif intent == IntentType.UPDATE_TODO:
            return self.handle_update_todo(parsed_command)
        elif intent == IntentType.COMPLETE_TODO:
            return self.handle_complete_todo(parsed_command)
        elif intent == IntentType.LIST_TODOS:
            return self.handle_list_todos(parsed_command)
        else:
            return {
                'success': False,
                'operation_type': 'UNKNOWN',
                'message': f'Unknown command intent: {intent}',
                'parsed_command': parsed_command.to_dict()
            }

    def handle_add_todo(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """
        Handle adding a new todo
        Enhanced to handle separate title and description entities
        """
        try:
            # Extract task title and description from entities
            title = None
            description = ""

            # First, look for explicit task_title entity (from complex patterns)
            for entity in parsed_command.entities:
                if entity['type'] == 'task_title':
                    title = entity['value'].strip().capitalize()
                elif entity['type'] == 'task_description':
                    description = entity['value'].strip().capitalize()

            # If we still don't have a title, try to extract from task_description
            if not title:
                for entity in parsed_command.entities:
                    if entity['type'] == 'task_description':
                        desc_value = entity['value'].strip()

                        # Try to split into title and description if there are multiple parts
                        if ' - ' in desc_value:
                            parts = desc_value.split(' - ', 1)
                            title = parts[0].strip().capitalize()
                            description = parts[1].strip().capitalize()
                        elif ':' in desc_value:
                            parts = desc_value.split(':', 1)
                            title = parts[0].strip().capitalize()
                            description = parts[1].strip().capitalize()
                        else:
                            title = desc_value.capitalize()

            if not title:
                # Try to extract title from the raw input if not found in entities
                title = self._extract_title_from_raw(parsed_command.raw_input)

            if not title:
                return {
                    'success': False,
                    'operation_type': 'ADD',
                    'message': 'Could not determine task title from your command. Please be more specific.',
                    'suggestions': ['Include a clear task title in your command', 'Use phrases like "add a task to..."']
                }

            # Create the task
            task = self.todo_ops_service.create_task(title, description)

            if description:
                message = f'Successfully added task: "{task.title}" with description: "{task.description}"'
            else:
                message = f'Successfully added task: "{task.title}"'

            return {
                'success': True,
                'operation_type': 'ADD',
                'message': message,
                'affected_task': task.to_dict(),
                'parsed_command': parsed_command.to_dict()
            }

        except Exception as e:
            return {
                'success': False,
                'operation_type': 'ADD',
                'message': f'Error adding task: {str(e)}',
                'parsed_command': parsed_command.to_dict()
            }

    def handle_delete_todo(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """
        Handle deleting a todo
        """
        try:
            # Find the task to delete based on identifiers in the command
            target_task = None

            # Check if we have a context reference (like "that one", "the last one")
            if parsed_command.context_reference:
                target_task = self.todo_ops_service.find_task_by_reference(parsed_command.context_reference)

            # If no context reference or it didn't resolve, try to find by entity
            if not target_task:
                for entity in parsed_command.entities:
                    if entity['type'] == 'task_identifier':
                        target_task = self.todo_ops_service.find_task_by_identifier(entity['value'], self.user_id)
                        if target_task:
                            break

            # If still no task found, try to match from raw input
            if not target_task:
                target_task = self.todo_ops_service.find_task_by_identifier(parsed_command.raw_input, self.user_id)

            if not target_task:
                return {
                    'success': False,
                    'operation_type': 'DELETE',
                    'message': 'Could not find the task to delete. Could you be more specific?',
                    'suggestions': ['Mention the exact task title', 'Specify which task you want to delete']
                }

            # Delete the task
            self.todo_ops_service.delete_task(target_task.id)

            return {
                'success': True,
                'operation_type': 'DELETE',
                'message': f'Successfully deleted task: "{target_task.title}"',
                'affected_task': target_task.to_dict(),
                'parsed_command': parsed_command.to_dict()
            }

        except Exception as e:
            return {
                'success': False,
                'operation_type': 'DELETE',
                'message': f'Error deleting task: {str(e)}',
                'parsed_command': parsed_command.to_dict()
            }

    def handle_update_todo(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """
        Handle updating a todo
        """
        try:
            # Find the task to update
            target_task = None

            # Check if we have a context reference
            if parsed_command.context_reference:
                target_task = self.todo_ops_service.find_task_by_reference(parsed_command.context_reference)

            # If no context reference or it didn't resolve, try to find by entity
            if not target_task:
                for entity in parsed_command.entities:
                    if entity['type'] == 'task_identifier':
                        target_task = self.todo_ops_service.find_task_by_identifier(entity['value'], self.user_id)
                        if target_task:
                            break

            if not target_task:
                return {
                    'success': False,
                    'operation_type': 'UPDATE',
                    'message': 'Could not find the task to update. Could you be more specific?',
                    'suggestions': ['Mention the exact task title', 'Specify which task you want to update']
                }

            # Extract new values from the command
            new_title = None
            new_description = None
            new_status = None

            # This is a simplified approach - in a real implementation,
            # we would have more sophisticated parsing for update commands
            raw_input = parsed_command.raw_input.lower()

            # Look for status changes
            if 'complete' in raw_input or 'done' in raw_input:
                new_status = 'Completed'
            elif 'pending' in raw_input or 'incomplete' in raw_input:
                new_status = 'Pending'

            # For now, we'll just return a message indicating the update was attempted
            updated_task = self.todo_ops_service.update_task(
                target_task.id,
                title=new_title,
                description=new_description,
                status=new_status
            )

            status_msg = f' and marked as {new_status}' if new_status else ''
            return {
                'success': True,
                'operation_type': 'UPDATE',
                'message': f'Successfully updated task: "{updated_task.title}"{status_msg}',
                'affected_task': updated_task.to_dict(),
                'parsed_command': parsed_command.to_dict()
            }

        except Exception as e:
            return {
                'success': False,
                'operation_type': 'UPDATE',
                'message': f'Error updating task: {str(e)}',
                'parsed_command': parsed_command.to_dict()
            }

    def handle_complete_todo(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """
        Handle completing a todo
        """
        try:
            # Find the task to complete
            target_task = None

            # Check if we have a context reference
            if parsed_command.context_reference:
                target_task = self.todo_ops_service.find_task_by_reference(parsed_command.context_reference)

            # If no context reference or it didn't resolve, try to find by entity
            if not target_task:
                for entity in parsed_command.entities:
                    if entity['type'] == 'task_identifier':
                        target_task = self.todo_ops_service.find_task_by_identifier(entity['value'], self.user_id)
                        if target_task:
                            break

            # If still no task found, try to match from raw input
            if not target_task:
                target_task = self.todo_ops_service.find_task_by_identifier(parsed_command.raw_input, self.user_id)

            if not target_task:
                return {
                    'success': False,
                    'operation_type': 'COMPLETE',
                    'message': 'Could not find the task to complete. Could you be more specific?',
                    'suggestions': ['Mention the exact task title', 'Specify which task you want to complete']
                }

            # Complete the task
            completed_task = self.todo_ops_service.update_task(target_task.id, status='Completed')

            return {
                'success': True,
                'operation_type': 'COMPLETE',
                'message': f'Successfully completed task: "{completed_task.title}"',
                'affected_task': completed_task.to_dict(),
                'parsed_command': parsed_command.to_dict()
            }

        except Exception as e:
            return {
                'success': False,
                'operation_type': 'COMPLETE',
                'message': f'Error completing task: {str(e)}',
                'parsed_command': parsed_command.to_dict()
            }

    def handle_list_todos(self, parsed_command: ParsedCommand) -> Dict[str, Any]:
        """
        Handle listing todos
        """
        try:
            # Determine filters based on command
            status_filter = None
            for entity in parsed_command.entities:
                if entity['type'] == 'filter_status':
                    status_filter = entity['value']
                    break

            # Get tasks based on filters
            tasks = self.todo_ops_service.list_tasks(status=status_filter)

            if not tasks:
                status_msg = f' {status_filter.lower()}' if status_filter else ''
                return {
                    'success': True,
                    'operation_type': 'LIST',
                    'message': f'You have no{status_msg} tasks.',
                    'affected_task': None,
                    'parsed_command': parsed_command.to_dict()
                }

            # Format the response
            task_titles = [f'• {task.title}' for task in tasks]
            status_msg = f' {status_filter.lower()}' if status_filter else ' all'
            message = f'Here are your{status_msg} tasks:\n' + '\n'.join(task_titles)

            return {
                'success': True,
                'operation_type': 'LIST',
                'message': message,
                'affected_task': None,
                'parsed_command': parsed_command.to_dict(),
                'task_list': [task.to_dict() for task in tasks]
            }

        except Exception as e:
            return {
                'success': False,
                'operation_type': 'LIST',
                'message': f'Error listing tasks: {str(e)}',
                'parsed_command': parsed_command.to_dict()
            }

    def format_response(self, result: Dict[str, Any], parsed_command: ParsedCommand) -> Dict[str, Any]:
        """
        Format the response in the required structure
        """
        # Set the operation performed based on the result
        operation_map = {
            'ADD': 'ADD',
            'DELETE': 'DELETE',
            'UPDATE': 'UPDATE',
            'COMPLETE': 'COMPLETE',
            'LIST': 'LIST'
        }

        operation_performed = operation_map.get(result.get('operation_type', 'UNKNOWN'), 'UNKNOWN')

        return {
            'success': result.get('success', False),
            'operation_performed': operation_performed,
            'message': result.get('message', 'Operation completed'),
            'parsed_command': result.get('parsed_command', parsed_command.to_dict()),
            'affected_task': result.get('affected_task'),
            'task_list': result.get('task_list', []),
            'suggested_next_steps': self._suggest_next_steps(operation_performed)
        }

    def _extract_title_from_raw(self, raw_input: str) -> Optional[str]:
        """
        Extract task title from raw input if not found in entities
        """
        # Remove common command verbs and prepositions
        text = raw_input.lower()
        for verb in ['add', 'create', 'make', 'new', 'a', 'an', 'the', 'to', 'for', 'about']:
            text = re.sub(r'\b' + verb + r'\b', '', text, flags=re.IGNORECASE)

        # Clean up extra spaces
        text = ' '.join(text.split())

        # If the remaining text is substantial, consider it as the title
        if len(text) > 3:  # At least 3 characters
            return text.strip().capitalize()

        return None

    def _suggest_next_steps(self, operation_performed: str) -> list:
        """
        Suggest next steps based on the operation performed
        """
        suggestions = {
            'ADD': ['You can add more tasks', 'You can list your tasks', 'You can mark tasks as complete'],
            'DELETE': ['You can add new tasks', 'You can list your remaining tasks', 'You can update other tasks'],
            'UPDATE': ['You can list your tasks', 'You can mark tasks as complete', 'You can add more tasks'],
            'COMPLETE': ['You can list your pending tasks', 'You can add new tasks', 'You can update other tasks'],
            'LIST': ['You can add new tasks', 'You can mark tasks as complete', 'You can delete tasks']
        }

        return suggestions.get(operation_performed, ['You can manage your tasks using natural language'])


# Global instance for convenience
command_processor = None


def get_command_processor(db_session: Session, user_id: str) -> CommandProcessor:
    """
    Factory function to get a command processor instance with proper dependencies
    """
    return CommandProcessor(db_session, user_id)