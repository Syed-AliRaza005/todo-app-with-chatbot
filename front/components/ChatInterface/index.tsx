'use client';

import { useState, useEffect, useRef } from 'react';
import { ChatWindow } from './ChatWindow';
import { ChatSidebar } from './ChatSidebar';
import { MessageInput } from './MessageInput';
import { UIState } from '@/types/ui-state';
import { ChatSession } from '@/types/session';
import { Message } from '@/types/message';
import mcpClient from '@/lib/mcp-client';
import { useAuth } from '@/hooks/useAuth';

interface ChatInterfaceProps {
  isWidget?: boolean;
}

export const ChatInterface = ({ isWidget = false }: ChatInterfaceProps) => {
  const { user, isLoading: authLoading } = useAuth();
  const [uiState, setUiState] = useState<UIState>({
    activeSessionId: '',
    inputValue: '',
    isLoading: false,
    showSidebar: !isWidget, // Hide sidebar in widget mode
    unreadCount: 0,
  });

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Initialize the chat interface
  useEffect(() => {
    loadInitialData();
  }, [user]); // Reload when auth state changes

  const loadInitialData = async () => {
    if (authLoading || !user) {
      setUiState(prev => ({ ...prev, isLoading: false }));
      return;
    }

    try {
      setUiState(prev => ({ ...prev, isLoading: true }));

      // Load chat sessions for the authenticated user
      const sessionData = await mcpClient.getSessions();
      const mappedSessions: ChatSession[] = sessionData.sessions
        .filter((session: any) => !session.user_id || session.user_id === user?.id) // Only show user's sessions
        .map((session: any) => ({
          id: session.id,
          title: session.title || `Chat ${session.id.substring(0, 8)}`,
          createdAt: new Date(session.created_at || session.createdAt),
          updatedAt: new Date(session.updated_at || session.updatedAt),
          isActive: session.isActive || false,
        }));

      setSessions(mappedSessions);

      // Set the first session as active if available
      if (mappedSessions.length > 0) {
        const firstSession = mappedSessions[0];
        setActiveSession(firstSession);
        setUiState(prev => ({ ...prev, activeSessionId: firstSession.id }));

        // Load messages for the active session
        await loadMessages(firstSession.id);
      } else {
        // If no sessions exist, clear messages
        setMessages([]);
      }

      setUiState(prev => ({ ...prev, isLoading: false }));
    } catch (error) {
      console.error('Error loading initial data:', error);
      setUiState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const loadMessages = async (sessionId: string) => {
    try {
      setUiState(prev => ({ ...prev, isLoading: true }));

      const messageData = await mcpClient.getSessionMessages(sessionId);
      const mappedMessages: Message[] = messageData.messages.map((msg: any) => ({
        id: msg.id,
        sessionId: msg.session_id || msg.sessionId,
        sender: (msg.sender || msg.role) as 'user' | 'assistant',
        content: msg.content,
        timestamp: new Date(msg.timestamp),
        status: (msg.status || 'sent') as 'sent' | 'delivered' | 'read' | 'failed',
      }));

      setMessages(mappedMessages);
      setUiState(prev => ({ ...prev, isLoading: false }));
    } catch (error) {
      console.error('Error loading messages:', error);
      setUiState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    try {
      // Optimistically update UI with the new message
      const newMessage: Message = {
        id: `temp-${Date.now()}`,
        sessionId: uiState.activeSessionId,
        sender: 'user',
        content: content,
        timestamp: new Date(),
        status: 'sent',
      };

      setMessages(prev => [...prev, newMessage]);
      setUiState(prev => ({ ...prev, inputValue: '', isLoading: true }));

      // Send to MCP service with user ID
      const response = await mcpClient.sendMessage({
        message: content,
        session_id: uiState.activeSessionId,
        user_id: user?.id, // Pass user ID to associate with user
      });

      // Update session ID if it changed
      if (response.session_id !== uiState.activeSessionId) {
        setUiState(prev => ({ ...prev, activeSessionId: response.session_id }));

        // Refresh sessions to show the new one
        loadInitialData();
      }

      // Replace the optimistic message with the actual one
      setMessages(prev => prev.map(msg =>
        msg.id.startsWith('temp-') ? {
          ...msg,
          id: `${msg.id}_sent`,
          sessionId: response.session_id
        } : msg
      ));

      // Add the assistant's response
      const assistantMessage: Message = {
        id: `resp_${Date.now()}`,
        sessionId: response.session_id,
        sender: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp),
        status: 'sent',
      };

      setMessages(prev => [...prev, assistantMessage]);
      setUiState(prev => ({ ...prev, isLoading: false }));
    } catch (error) {
      console.error('Error sending message:', error);
      setUiState(prev => ({ ...prev, isLoading: false }));

      // Remove the optimistic message on error
      setMessages(prev => prev.filter(msg => !msg.id.startsWith('temp-')));

      // Show error in UI
      alert('Failed to send message. Please try again.');
    }
  };

  const handleSessionChange = async (sessionId: string) => {
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
      setActiveSession(session);
      setUiState(prev => ({ ...prev, activeSessionId: sessionId }));
      await loadMessages(sessionId);
    }
  };

  const handleNewSession = async () => {
    if (!user) {
      alert('Please log in to create a chat session.');
      return;
    }

    try {
      setUiState(prev => ({ ...prev, isLoading: true }));

      // Create new session via API with user ID
      const newSessionData = await mcpClient.createNewSession(user.id);

      const newSession: ChatSession = {
        id: newSessionData.id,
        title: newSessionData.title,
        createdAt: new Date(newSessionData.created_at),
        updatedAt: new Date(newSessionData.updated_at),
        isActive: true,
      };

      setSessions(prev => [newSession, ...prev]);
      setActiveSession(newSession);
      setMessages([]);
      setUiState(prev => ({
        ...prev,
        activeSessionId: newSession.id,
        inputValue: '',
        isLoading: false
      }));
    } catch (error) {
      console.error('Error creating new session:', error);
      setUiState(prev => ({ ...prev, isLoading: false }));

      // Show error to user
      alert('Failed to create new session. Please try again.');
    }
  };

  return (
    <div className={`${isWidget ? 'h-full' : 'h-screen'} flex bg-gray-50`}>
      {/* Sidebar - hidden in widget mode */}
      {!isWidget && (
        <div className={`${uiState.showSidebar ? 'w-64 md:w-80' : 'hidden'} flex-shrink-0 border-r border-gray-200 bg-white`}>
          <ChatSidebar
            sessions={sessions}
            activeSession={activeSession}
            onSessionChange={handleSessionChange}
            onNewSession={handleNewSession}
            unreadCount={uiState.unreadCount}
          />
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex flex-col flex-1">
        {/* Chat Window */}
        <div className="flex-1 overflow-y-auto">
          <ChatWindow
            messages={messages}
            isLoading={uiState.isLoading}
            activeSession={activeSession}
          />
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="border-t border-gray-200 bg-white p-4">
          <MessageInput
            value={uiState.inputValue}
            onChange={(value) => setUiState(prev => ({ ...prev, inputValue: value }))}
            onSend={handleSendMessage}
            disabled={uiState.isLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;