from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging
import random
import re
import time
from datetime import datetime
from sqlmodel import Session, select
from .database import get_db
from .models.chat import ChatSession, ChatMessage as DBChatMessage, ChatMessageType
from .models.task import Task
from .models.user import User
from uuid import UUID
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define request/response models
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    success: bool


# Create router
router = APIRouter(prefix="/chat", tags=["chatbot"])


class SimpleChatbot:
    """
    A simple rule-based chatbot that can handle basic conversations.
    """

    def __init__(self):
        self.responses = {
            'greeting': [
                "Hello! How can I assist you today?",
                "Hi there! What can I help you with?",
                "Greetings! Feel free to ask me anything."
            ],
            'goodbye': [
                "Goodbye! Have a great day!",
                "See you later! Take care!",
                "Farewell! Come back anytime."
            ],
            'thanks': [
                "You're welcome!",
                "Happy to help!",
                "Anytime!"
            ],
            'todo_help': [
                "I can help you manage your todos! You can add, list, update, or delete tasks.",
                "Need help with your tasks? Just let me know what you'd like to do!",
                "I'm here to help with your todo management!"
            ],
            'question': [
                "That's a good question! Let me think...",
                "I understand you're asking about this. Here's what I know:",
                "Great question! Here's what I can tell you:"
            ],
            'command': [
                "I'll help you with that task.",
                "Got it! I can assist you with that.",
                "Understood. Let me help you with that."
            ],
            'casual': [
                "Interesting! Tell me more about that.",
                "That's nice to hear. How else can I assist?",
                "Thanks for sharing! What else is on your mind?"
            ],
            'default': [
                "That's interesting! Tell me more.",
                "I understand. How else can I assist you?",
                "Thanks for sharing. What else would you like to know?",
                "I'm here to help with your todo management. What would you like to do?",
                "Could you clarify what you're looking for?"
            ]
        }

        # Patterns for recognizing different message types
        self.patterns = {
            'greeting': [
                r'hello', r'hi', r'hey', r'greetings', r'morning', r'afternoon', r'evening'
            ],
            'goodbye': [
                r'bye', r'goodbye', r'farewell', r'see you', r'ciao', r'good night'
            ],
            'thanks': [
                r'thanks', r'thank you', r'thx', r'appreciate', r'grateful'
            ],
            'todo_help': [
                r'todo', r'task', r'list', r'add', r'delete', r'update', r'manage', r'help'
            ],
            'question': [
                r'\?$|how.*\?|what.*\?|when.*\?|where.*\?|why.*\?|who.*\?|can you|could you|would you|do you|does.*',
                r'what is|what are|how do|explain|tell me about|help me with'
            ],
            'command': [
                r'please ', r'can you ', r'could you ', r'would you ', r'help me ',
                r'add ', r'create ', r'delete ', r'remove ', r'update ', r'change ', r'modify '
            ],
            'casual': [
                r'i am|i\'m|i am feeling|today i|just wanted to say|anyway,|btw,|by the way',
                r'cool|awesome|great|nice|wonderful|fantastic|interesting'
            ]
        }

    def recognize_intent(self, message: str) -> str:
        """
        Recognize the intent of the user message using pattern matching.
        Enhanced to handle different message types: questions, commands, casual statements.
        """
        message_lower = message.lower()

        # Check for specific intent patterns
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent

        # If no specific pattern matched, return default
        return 'default'

    def generate_response(self, message: str) -> str:
        """
        Generate a response based on the recognized intent.
        Enhanced to provide more appropriate responses for different message types.
        """
        intent = self.recognize_intent(message)

        # Handle specific todo-related intents
        if intent == 'todo_help':
            # Check if the message is specifically asking to list tasks
            message_lower = message.lower()
            if any(word in message_lower for word in ['list', 'show', 'display', 'see', 'view']):
                # This would normally return a special response to trigger API call
                # For now, return a placeholder response
                if 'pending' in message_lower or 'incomplete' in message_lower:
                    return "I can help you list your pending tasks. For actual task listing, the system would connect to the todo API."
                elif 'completed' in message_lower or 'done' in message_lower:
                    return "I can help you list your completed tasks. For actual task listing, the system would connect to the todo API."
                else:
                    return "I can help you list your tasks. For actual task listing, the system would connect to the todo API."

            # Handle other todo-related commands
            elif any(word in message_lower for word in ['add', 'create', 'new']):
                return "I can help you add a new task. For actual task creation, the system would connect to the todo API."

            elif any(word in message_lower for word in ['delete', 'remove', 'del']):
                return "I can help you delete a task. For actual task deletion, the system would connect to the todo API."

        if intent in self.responses:
            response = random.choice(self.responses[intent])

            # For questions, prepend an informative response
            if intent == 'question':
                return f"{random.choice(self.responses['question'])} {response}"
            # For commands, provide helpful assistance
            elif intent == 'command':
                return f"{random.choice(self.responses['command'])} {response}"
            # For casual statements, be conversational
            elif intent == 'casual':
                return f"{random.choice(self.responses['casual'])} {response}"
            else:
                return response
        else:
            return random.choice(self.responses['default'])


# Initialize the chatbot
chatbot = SimpleChatbot()


@router.post("/message", response_model=ChatResponse)
async def chat_message(chat_message: ChatMessageRequest, db: Session = Depends(get_db)):
    """
    Process a chat message and return a response from the chatbot.
    Includes comprehensive logging and response time tracking.
    """
    start_time = time.time()

    try:
        # Add input validation for message length
        if len(chat_message.message) > 10000:  # Max 10k characters
            logger.warning(f"Message too long from session {chat_message.session_id}: {len(chat_message.message)} characters")
            raise HTTPException(status_code=422, detail="Message exceeds maximum length of 10,000 characters")

        if len(chat_message.message.strip()) == 0:
            logger.warning(f"Empty message received from session {chat_message.session_id}")
            raise HTTPException(status_code=422, detail="Message cannot be empty")

        logger.info(f"Received message from session {chat_message.session_id}: {chat_message.message[:50]}{'...' if len(chat_message.message) > 50 else ''}")

        # Check if this is a todo-related command that requires API integration
        message_lower = chat_message.message.lower()

        # Only get user_id if the user exists in the database
        user_id = None
        if chat_message.user_id:
            try:
                user_obj = db.get(User, UUID(chat_message.user_id))
                if user_obj:
                    user_id = UUID(chat_message.user_id)
            except:
                user_id = None

        response_text = ""

        # Check if the user wants to list their tasks
        if any(word in message_lower for word in ['list', 'show', 'display', 'see', 'view']) and any(word in message_lower for word in ['task', 'todo', 'item', 'things']):
            if user_id:
                # Query tasks for the user
                if 'pending' in message_lower or 'incomplete' in message_lower:
                    tasks_query = select(Task).where(Task.user_id == user_id, Task.status == "Pending")
                elif 'completed' in message_lower or 'done' in message_lower:
                    tasks_query = select(Task).where(Task.user_id == user_id, Task.status == "Completed")
                else:
                    tasks_query = select(Task).where(Task.user_id == user_id)

                tasks = db.exec(tasks_query.order_by(Task.created_at.desc())).all()

                if tasks:
                    task_list = "\n".join([f"- {task.title}" for task in tasks])
                    response_text = f"Here are your tasks:\n{task_list}"
                else:
                    status_desc = ""
                    if 'pending' in message_lower:
                        status_desc = "pending "
                    elif 'completed' in message_lower:
                        status_desc = "completed "
                    response_text = f"You don't have any {status_desc}tasks right now."
            else:
                response_text = "I can help you list your tasks, but you need to be logged in to see your personal tasks."

        # Check if the user wants to add a task
        elif any(word in message_lower for word in ['add', 'create', 'new', 'make']) and any(word in message_lower for word in ['task', 'todo', 'item']):
            if user_id:
                # Extract task title from the message (simple extraction)
                # Look for patterns like "add task to buy groceries" or "create todo finish report"
                import re
                patterns = [
                    r'(?:add|create|make).*?(?:task|todo|item)\s+(?:to|for|about)?\s*(.+)',
                    r'(?:add|create|make)\s+(.+?)\s+(?:as\s+)?(?:a\s+)?(?:task|todo|item)'
                ]

                task_title = None
                for pattern in patterns:
                    match = re.search(pattern, message_lower)
                    if match:
                        task_title = match.group(1).strip().capitalize()
                        break

                # If we couldn't extract using patterns, try a simpler approach
                if not task_title:
                    # Remove common command words and get the remainder
                    words = message_lower.split()
                    # Find the first occurrence of task/todo and take everything after
                    for i, word in enumerate(words):
                        if word in ['task', 'todo', 'item']:
                            if i + 1 < len(words):
                                task_title = ' '.join(words[i+1:]).strip().capitalize()
                                break

                if task_title and len(task_title) > 0:
                    # Create a new task
                    new_task = Task(
                        user_id=user_id,
                        title=task_title,
                        description="",  # Could extract description if needed
                        status="Pending"
                    )
                    db.add(new_task)
                    db.commit()
                    db.refresh(new_task)
                    response_text = f"I've added the task: '{task_title}' to your list."
                else:
                    response_text = "I couldn't understand what task you want to add. Please be more specific, like 'add a task to buy groceries'."
            else:
                response_text = "I can help you add a task, but you need to be logged in first."

        # Check if the user wants to delete a task
        elif any(word in message_lower for word in ['delete', 'remove', 'finish', 'complete']) and any(word in message_lower for word in ['task', 'todo', 'item']):
            if user_id:
                # For simplicity, we'll just mark as complete if 'finish' or 'complete' is mentioned
                is_completion = any(word in message_lower for word in ['finish', 'complete', 'done'])

                # Extract potential task reference
                # Look for patterns like "delete task buy groceries" or "complete the meeting task"
                import re
                # Simple approach: get words after the command word
                words = message_lower.split()
                task_keyword_idx = -1
                for i, word in enumerate(words):
                    if word in ['task', 'todo', 'item']:
                        task_keyword_idx = i
                        break

                if task_keyword_idx != -1 and task_keyword_idx + 1 < len(words):
                    task_reference = ' '.join(words[task_keyword_idx + 1:]).strip()

                    # Find a task that matches the reference
                    if is_completion:
                        # Find pending tasks that match the reference
                        tasks_query = select(Task).where(
                            Task.user_id == user_id,
                            Task.status == "Pending",
                            Task.title.ilike(f'%{task_reference}%')
                        )
                    else:
                        # Find any task that matches the reference
                        tasks_query = select(Task).where(
                            Task.user_id == user_id,
                            Task.title.ilike(f'%{task_reference}%')
                        )

                    matching_tasks = db.exec(tasks_query).all()

                    if matching_tasks:
                        target_task = matching_tasks[0]  # Take the first match

                        if is_completion:
                            target_task.status = "Completed"
                            target_task.completed_at = datetime.utcnow()
                            db.add(target_task)
                            db.commit()
                            response_text = f"I've marked the task '{target_task.title}' as completed."
                        else:
                            db.delete(target_task)
                            db.commit()
                            response_text = f"I've removed the task: '{target_task.title}'."
                    else:
                        action = "complete" if is_completion else "delete"
                        response_text = f"I couldn't find a task matching '{task_reference}' to {action}."
                else:
                    action = "completing" if is_completion else "deleting"
                    response_text = f"To {action} a task, please specify which one, like 'complete the meeting task' or 'delete buy groceries task'."
            else:
                action = "complete" if any(word in message_lower for word in ['finish', 'complete', 'done']) else "delete"
                response_text = f"I can help you {action} a task, but you need to be logged in first."

        # If not a special command, use the chatbot's standard response
        if not response_text:
            response_text = chatbot.generate_response(chat_message.message)

        # Get or create session
        session_id = None
        if chat_message.session_id:
            try:
                session_uuid = UUID(chat_message.session_id)
                existing_session = db.get(ChatSession, session_uuid)
                if existing_session:
                    session_id = session_uuid
                    # Update session with new timestamp and last message
                    existing_session.updated_at = datetime.utcnow()
                    existing_session.last_message = chat_message.message[:50] + ('...' if len(chat_message.message) > 50 else '')
                    db.add(existing_session)
                else:
                    # Create new session with provided ID
                    # Only set user_id if the user actually exists in the users table
                    user_id_for_session = None
                    if chat_message.user_id:
                        try:
                            # Check if user exists before setting the foreign key
                            user_exists = db.get(User, UUID(chat_message.user_id))
                            if user_exists:
                                user_id_for_session = UUID(chat_message.user_id)
                        except:
                            # If there's an error checking user existence, don't set user_id
                            user_id_for_session = None

                    session_id = session_uuid
                    new_session = ChatSession(
                        id=session_id,
                        title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        user_id=user_id_for_session,
                        last_message=chat_message.message[:50] + ('...' if len(chat_message.message) > 50 else '')
                    )
                    db.add(new_session)
            except ValueError:
                # Invalid UUID format, create new session
                session_id = uuid.uuid4()
                new_session = ChatSession(
                    id=session_id,
                    title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    user_id=UUID(chat_message.user_id) if chat_message.user_id else None,
                    last_message=chat_message.message[:50] + ('...' if len(chat_message.message) > 50 else '')
                )
                db.add(new_session)
        else:
            # Create new session
            user_id_for_session = None
            if chat_message.user_id:
                try:
                    # Check if user exists before setting the foreign key
                    user_exists = db.get(User, UUID(chat_message.user_id))
                    if user_exists:
                        user_id_for_session = UUID(chat_message.user_id)
                except:
                    # If there's an error checking user existence, don't set user_id
                    user_id_for_session = None

            session_id = uuid.uuid4()
            new_session = ChatSession(
                id=session_id,
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                user_id=user_id_for_session,
                last_message=chat_message.message[:50] + ('...' if len(chat_message.message) > 50 else '')
            )
            db.add(new_session)

        # Create user message record
        user_message = DBChatMessage(
            session_id=session_id,
            sender=ChatMessageType.USER,
            content=chat_message.message,
            status="sent"
        )
        db.add(user_message)

        # Create assistant response record
        assistant_message = DBChatMessage(
            session_id=session_id,
            sender=ChatMessageType.ASSISTANT,
            content=response_text,
            status="sent"
        )
        db.add(assistant_message)

        # Commit all changes
        db.commit()

        # Create response
        response = ChatResponse(
            response=response_text,
            session_id=str(session_id),
            timestamp=datetime.now().isoformat(),
            success=True
        )

        # Calculate response time
        response_time = time.time() - start_time

        # Log comprehensive interaction data
        logger.info(f"Chat interaction completed - Session: {session_id}, Response time: {response_time:.3f}s, Message: {chat_message.message[:30]}{'...' if len(chat_message.message) > 30 else ''}")

        return response

    except HTTPException as e:
        response_time = time.time() - start_time
        logger.error(f"HTTP error in chat processing - Session: {chat_message.session_id}, Response time: {response_time:.3f}s, Error: {str(e.detail)}")
        db.rollback()
        raise
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"Unexpected error in chat processing - Session: {chat_message.session_id}, Response time: {response_time:.3f}s, Error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")


@router.get("/sessions")
async def get_sessions(db: Session = Depends(get_db)):
    """
    Get all chat sessions.
    """
    try:
        # Query all sessions from database
        statement = select(ChatSession).order_by(ChatSession.updated_at.desc())
        results = db.exec(statement)
        db_sessions = results.all()

        # Convert sessions to response format
        sessions_list = []
        for db_session in db_sessions:
            sessions_list.append({
                'id': str(db_session.id),
                'title': db_session.title,
                'created_at': db_session.created_at.isoformat() if db_session.created_at else None,
                'updated_at': db_session.updated_at.isoformat() if db_session.updated_at else None,
                'last_message_preview': db_session.last_message or '',
                'unread_count': 0  # For simplicity, we're not tracking unread messages
            })

        return {
            'sessions': sessions_list,
            'total': len(sessions_list)
        }
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """
    Get messages for a specific session.
    """
    try:
        # Validate session_id format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid session ID format")

        # Query messages for the session from database
        statement = select(DBChatMessage).where(DBChatMessage.session_id == session_uuid).order_by(DBChatMessage.timestamp.asc())
        results = db.exec(statement)
        db_messages = results.all()

        # Convert messages to response format
        messages_list = []
        for db_message in db_messages:
            messages_list.append({
                'id': str(db_message.id),
                'session_id': str(db_message.session_id),
                'sender': db_message.sender.value,
                'content': db_message.content,
                'timestamp': db_message.timestamp.isoformat() if db_message.timestamp else None,
                'status': db_message.status
            })

        return {
            'messages': messages_list,
            'total': len(messages_list),
            'session_id': session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching messages for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {str(e)}")


@router.post("/sessions")
async def create_session(db: Session = Depends(get_db)):
    """
    Create a new chat session.
    """
    try:
        session_id = uuid.uuid4()

        new_session = ChatSession(
            id=session_id,
            title=f"New Chat {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_message=""
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return {
            'id': str(new_session.id),
            'title': new_session.title,
            'created_at': new_session.created_at.isoformat() if new_session.created_at else None,
            'updated_at': new_session.updated_at.isoformat() if new_session.updated_at else None
        }
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.get("/health")
async def chatbot_health():
    """
    Health check for the chatbot service.
    """
    return {
        "status": "healthy",
        "service": "chatbot",
        "message": "Chatbot service is running"
    }


@router.post("/reset-session")
async def reset_session(session_id: str, db: Session = Depends(get_db)):
    """
    Reset a specific chat session by clearing its messages.
    """
    try:
        # Validate session_id format
        try:
            session_uuid = UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid session ID format")

        # Verify session exists
        existing_session = db.get(ChatSession, session_uuid)
        if not existing_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Delete all messages associated with this session
        statement = select(DBChatMessage).where(DBChatMessage.session_id == session_uuid)
        results = db.exec(statement)
        messages_to_delete = results.all()

        for message in messages_to_delete:
            db.delete(message)

        # Update session's last message
        existing_session.last_message = ""
        existing_session.updated_at = datetime.utcnow()
        db.add(existing_session)

        db.commit()

        return {
            "message": f"Session {session_id} has been reset",
            "session_id": session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting session {session_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error resetting session: {str(e)}")


# Additional utility functions
def get_bot_info():
    """
    Get information about the chatbot.
    """
    return {
        "name": "Simple Todo Assistant",
        "version": "1.0.0",
        "capabilities": [
            "Answer basic questions",
            "Provide todo management help",
            "Engage in light conversation"
        ]
    }


@router.get("/info")
async def bot_info():
    """
    Get information about the chatbot.
    """
    return get_bot_info()


# Example usage function (for testing)
def test_chatbot():
    """
    Test the chatbot with sample messages.
    """
    test_messages = [
        "Hello",
        "How are you?",
        "I need help with my todos",
        "Thank you",
        "Goodbye"
    ]

    print("Chatbot Test:")
    for msg in test_messages:
        response = chatbot.generate_response(msg)
        print(f"User: {msg}")
        print(f"Bot: {response}\n")


if __name__ == "__main__":
    # This would run tests if the file is executed directly
    test_chatbot()