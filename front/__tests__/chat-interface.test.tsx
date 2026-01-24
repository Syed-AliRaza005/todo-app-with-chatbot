// Unit tests for Chat Interface components
// Testing the core functionality of the chatbot UI

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

describe('ChatInterface Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders the chat interface with sidebar and main window', async () => {
    // Mock the API responses
    const mockSessions = [
      {
        id: 'session-1',
        title: 'Test Chat',
        createdAt: new Date(),
        updatedAt: new Date(),
        isActive: true,
      },
    ];

    const mockMessages = [
      {
        id: 'msg-1',
        sessionId: 'session-1',
        sender: 'assistant',
        content: 'Hello! How can I help you?',
        timestamp: new Date(),
        status: 'sent',
      },
    ];

    // @ts-ignore - mocking for tests
    const { mcpClient } = await import('@/lib/mcp-client');
    mcpClient.getSessions.mockResolvedValue(mockSessions);
    mcpClient.getSessionMessages.mockResolvedValue(mockMessages);

    render(<ChatInterface />);

    // Wait for the component to load
    await waitFor(() => {
      expect(screen.getByText('Test Chat')).toBeInTheDocument();
    });

    // Check if the main chat area is present
    expect(screen.getByText('Hello! How can I help you?')).toBeInTheDocument();

    // Check if the message input is present
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
  });

  it('allows sending a message', async () => {
    // Mock the API responses
    const mockSessions = [
      {
        id: 'session-1',
        title: 'Test Chat',
        createdAt: new Date(),
        updatedAt: new Date(),
        isActive: true,
      },
    ];

    const mockMessages = [
      {
        id: 'msg-1',
        sessionId: 'session-1',
        sender: 'assistant',
        content: 'Hello! How can I help you?',
        timestamp: new Date(),
        status: 'sent',
      },
    ];

    // @ts-ignore - mocking for tests
    const { mcpClient } = await import('@/lib/mcp-client');
    mcpClient.getSessions.mockResolvedValue(mockSessions);
    mcpClient.getSessionMessages.mockResolvedValue(mockMessages);
    mcpClient.sendMessage.mockResolvedValue({
      response: 'Thanks for your message!',
      sessionId: 'session-1',
      timestamp: new Date().toISOString(),
    });

    render(<ChatInterface />);

    // Wait for the component to load
    await waitFor(() => {
      expect(screen.getByText('Test Chat')).toBeInTheDocument();
    });

    // Find the input field and send a message
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByLabelText('Send message');

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    // Wait for the message to be processed
    await waitFor(() => {
      expect(mcpClient.sendMessage).toHaveBeenCalledWith({
        sessionId: 'session-1',
        message: 'Test message',
      });
    });
  });

  it('displays loading state while fetching data', async () => {
    // Mock the API to resolve after a delay
    const { mcpClient } = await import('@/lib/mcp-client');
    mcpClient.getSessions.mockImplementation(() => new Promise(resolve => {
      setTimeout(() => resolve([]), 100);
    }));

    render(<ChatInterface />);

    // Initially should show loading state
    expect(screen.getByText('No messages yet')).toBeInTheDocument();

    // Wait for the data to load
    await waitFor(() => {
      expect(screen.getByText('Send a message to start the conversation')).toBeInTheDocument();
    });
  });
});