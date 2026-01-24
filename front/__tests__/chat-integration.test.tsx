// Integration tests for Chat Interface
// Testing the main user flows of the chatbot UI

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ChatInterface } from '../components/ChatInterface';

// Mock the services and dependencies
vi.mock('@/lib/mcp-client', () => ({
  mcpClient: {
    getSessions: vi.fn(),
    getSessionMessages: vi.fn(),
    sendMessage: vi.fn(),
  },
}));

vi.mock('../services/session-service', () => ({
  sessionService: {
    getAllSessions: vi.fn(),
    createSession: vi.fn(),
  },
}));

vi.mock('../services/message-service', () => ({
  messageService: {
    getMessages: vi.fn(),
    sendMessage: vi.fn(),
  },
}));

describe('Chat Interface Integration Tests', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('creates a new session and allows messaging', async () => {
    // Mock empty initial state
    const mockEmptySessions = [];

    // @ts-ignore - mocking for tests
    const { mcpClient } = await import('@/lib/mcp-client');
    mcpClient.getSessions.mockResolvedValue(mockEmptySessions);
    mcpClient.getSessionMessages.mockResolvedValue([]);

    // Mock the response for a new session
    mcpClient.sendMessage.mockResolvedValue({
      response: 'Hello! How can I help you?',
      sessionId: 'session-1',
      timestamp: new Date().toISOString(),
    });

    render(<ChatInterface />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('No chat sessions yet')).toBeInTheDocument();
    });

    // Click to start a new conversation
    const newChatButton = screen.getByText('Start a new conversation');
    fireEvent.click(newChatButton);

    // Wait for the new session to be created and UI to update
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    });

    // Send a test message
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: 'Hello, world!' } });
    fireEvent.click(sendButton);

    // Wait for the message to be sent
    await waitFor(() => {
      expect(mcpClient.sendMessage).toHaveBeenCalledWith({
        sessionId: expect.any(String),
        message: 'Hello, world!',
      });
    });

    // Verify that the assistant responded
    expect(screen.getByText('Hello! How can I help you?')).toBeInTheDocument();
  });

  it('switches between existing sessions', async () => {
    // Mock sessions
    const mockSessions = [
      {
        id: 'session-1',
        title: 'First Chat',
        createdAt: new Date('2023-01-01'),
        updatedAt: new Date('2023-01-01'),
        isActive: false,
      },
      {
        id: 'session-2',
        title: 'Second Chat',
        createdAt: new Date('2023-01-02'),
        updatedAt: new Date('2023-01-02'),
        isActive: true,
      },
    ];

    const mockMessages1 = [
      {
        id: 'msg-1',
        sessionId: 'session-1',
        sender: 'user',
        content: 'Message from first chat',
        timestamp: new Date(),
        status: 'sent',
      },
    ];

    const mockMessages2 = [
      {
        id: 'msg-2',
        sessionId: 'session-2',
        sender: 'user',
        content: 'Message from second chat',
        timestamp: new Date(),
        status: 'sent',
      },
    ];

    // @ts-ignore - mocking for tests
    const { mcpClient } = await import('@/lib/mcp-client');
    mcpClient.getSessions.mockResolvedValue(mockSessions);
    mcpClient.getSessionMessages.mockImplementation(async (sessionId: string) => {
      if (sessionId === 'session-1') {
        return mockMessages1;
      }
      return mockMessages2;
    });

    render(<ChatInterface />);

    // Wait for sessions to load
    await waitFor(() => {
      expect(screen.getByText('First Chat')).toBeInTheDocument();
      expect(screen.getByText('Second Chat')).toBeInTheDocument();
    });

    // Verify current session is second chat
    expect(screen.getByText('Message from second chat')).toBeInTheDocument();

    // Switch to first session
    const firstChatButton = screen.getByText('First Chat');
    fireEvent.click(firstChatButton);

    // Wait for messages to load for first session
    await waitFor(() => {
      expect(screen.getByText('Message from first chat')).toBeInTheDocument();
    });
  });

  it('handles error scenarios gracefully', async () => {
    // @ts-ignore - mocking for tests
    const { mcpClient } = await import('@/lib/mcp-client');

    // Mock an error when fetching sessions
    mcpClient.getSessions.mockRejectedValue(new Error('Network error'));
    mcpClient.getSessionMessages.mockResolvedValue([]);

    render(<ChatInterface />);

    // Wait for error handling
    await waitFor(() => {
      // Component should still render despite error
      expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    });
  });
});