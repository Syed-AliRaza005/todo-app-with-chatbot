// Message Service for Chatbot UI
// Handles message-related operations for the chatbot interface

import { Message } from '@/types/message';
import { ChatAPIClient, ChatMessageRequest, ChatMessageResponse } from '@/lib/mcp-client';

class MessageService {
  private apiClient: ChatAPIClient;

  constructor() {
    this.apiClient = new ChatAPIClient();
  }

  /**
   * Send a message to the chatbot API
   */
  async sendMessage(sessionId: string, content: string): Promise<{ userMessage: Message; botMessage: Message }> {
    try {
      // Validate message content
      if (!content.trim()) {
        throw new Error('Message content cannot be empty');
      }

      if (content.length > 10000) {
        throw new Error('Message content exceeds maximum length of 10,000 characters');
      }

      // Create user message object
      const userMessage: Message = {
        id: `msg_${Date.now()}_user`,
        sessionId,
        sender: 'user',
        content,
        timestamp: new Date(),
        status: 'sent',
      };

      // Send to backend API
      const response = await this.apiClient.sendMessage({
        message: content,
        session_id: sessionId
      });

      // Create bot response message
      const botMessage: Message = {
        id: `msg_${Date.now()}_bot`,
        sessionId: response.session_id,
        sender: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp),
        status: 'sent',
      };

      return { userMessage, botMessage };
    } catch (error) {
      console.error(`Error sending message to session ${sessionId}:`, error);
      throw error;
    }
  }

  /**
   * Get messages for a session (placeholder - backend doesn't have this endpoint yet)
   */
  async getMessages(sessionId: string): Promise<Message[]> {
    // Note: The backend doesn't have a direct endpoint to retrieve session messages yet
    // In a real implementation, we would call the backend API to fetch stored messages
    // For now, we'll return an empty array and handle message history in the UI state
    console.warn('Backend does not have session message retrieval endpoint yet');
    return [];
  }

  /**
   * Validate message content before sending
   */
  validateMessage(content: string): { isValid: boolean; error?: string } {
    if (!content || content.trim().length === 0) {
      return { isValid: false, error: 'Message cannot be empty' };
    }

    if (content.length > 10000) {
      return { isValid: false, error: 'Message exceeds maximum length of 10,000 characters' };
    }

    return { isValid: true };
  }
}

export const messageService = new MessageService();
export default MessageService;