// Session Service for Chatbot UI
// Handles chat session-related operations

import { ChatAPIClient } from '@/lib/mcp-client';
import { ChatSession } from '@/types/session';

class SessionService {
  private apiClient: ChatAPIClient;

  constructor() {
    this.apiClient = new ChatAPIClient();
  }

  /**
   * Get all chat sessions for the user
   */
  async getSessions(): Promise<ChatSession[]> {
    try {
      // Note: The backend doesn't have a direct endpoint for sessions yet
      // In a real implementation, we would call the backend API to fetch stored sessions
      // For now, we'll return an empty array and handle session management in the UI state
      console.warn('Backend does not have session listing endpoint yet');
      return [];
    } catch (error) {
      console.error('Error fetching sessions:', error);
      throw error;
    }
  }

  /**
   * Create a new chat session
   */
  async createSession(title?: string): Promise<ChatSession> {
    try {
      // In a real implementation, this would call the backend to create a session
      // For now, we'll create a session object in the frontend
      const sessionId = `sess_${Date.now()}`;

      const newSession: ChatSession = {
        id: sessionId,
        title: title || `Chat ${new Date().toLocaleDateString()}`,
        createdAt: new Date(),
        updatedAt: new Date(),
        isActive: true,
      };

      return newSession;
    } catch (error) {
      console.error('Error creating session:', error);
      throw error;
    }
  }

  /**
   * Get a specific session by ID
   */
  async getSession(sessionId: string): Promise<ChatSession | null> {
    try {
      // Note: The backend doesn't have a direct endpoint to retrieve a specific session yet
      // For now, we'll return null and handle session data in the UI state
      console.warn('Backend does not have session detail endpoint yet');
      return null;
    } catch (error) {
      console.error(`Error fetching session ${sessionId}:`, error);
      throw error;
    }
  }

  /**
   * Update a session
   */
  async updateSession(sessionId: string, updates: Partial<ChatSession>): Promise<ChatSession> {
    try {
      // In a real implementation, this would call the backend to update a session
      // For now, we'll return a simulated updated session

      const updatedSession: ChatSession = {
        id: sessionId,
        title: updates.title || `Chat ${new Date().toLocaleDateString()}`,
        createdAt: updates.createdAt || new Date(),
        updatedAt: new Date(),
        isActive: updates.isActive ?? true,
      };

      return updatedSession;
    } catch (error) {
      console.error(`Error updating session ${sessionId}:`, error);
      throw error;
    }
  }

  /**
   * Delete a session
   */
  async deleteSession(sessionId: string): Promise<void> {
    try {
      // In a real implementation, this would call the backend to delete a session
      // For now, we'll just simulate the deletion
      console.log(`Session ${sessionId} deleted`);
    } catch (error) {
      console.error(`Error deleting session ${sessionId}:`, error);
      throw error;
    }
  }

  /**
   * Reset a session
   */
  async resetSession(sessionId: string): Promise<void> {
    try {
      // Call the backend to reset the session
      await fetch(`${this.apiClient['baseUrl']}/chat/reset-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch (error) {
      console.error(`Error resetting session ${sessionId}:`, error);
      throw error;
    }
  }
}

export const sessionService = new SessionService();
export default SessionService;