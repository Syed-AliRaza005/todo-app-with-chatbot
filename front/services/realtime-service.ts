// Real-time Service for Chatbot UI
// Handles real-time message updates from backend

import { Message } from '@/types/message';

type MessageCallback = (message: Message) => void;
type ConnectionStatusCallback = (status: 'connected' | 'disconnected' | 'connecting') => void;

class RealTimeService {
  private ws: WebSocket | null = null;
  private messageCallbacks: MessageCallback[] = [];
  private statusCallbacks: ConnectionStatusCallback[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 5000;
  private sessionId: string | null = null;

  /**
   * Connect to real-time updates for a specific session
   */
  connect(sessionId: string): void {
    this.sessionId = sessionId;

    // In a real implementation, this would connect to a WebSocket endpoint
    // For now, we'll simulate the connection

    console.log(`Connecting to real-time updates for session: ${sessionId}`);

    // Simulate connection status updates
    this.notifyStatusChange('connecting');

    // Simulate successful connection after a short delay
    setTimeout(() => {
      this.notifyStatusChange('connected');
      this.reconnectAttempts = 0; // Reset attempts on successful connection
    }, 1000);
  }

  /**
   * Disconnect from real-time updates
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.notifyStatusChange('disconnected');
    this.sessionId = null;
  }

  /**
   * Subscribe to new messages
   */
  onMessage(callback: MessageCallback): void {
    this.messageCallbacks.push(callback);
  }

  /**
   * Subscribe to connection status changes
   */
  onStatusChange(callback: ConnectionStatusCallback): void {
    this.statusCallbacks.push(callback);
  }

  /**
   * Remove message subscription
   */
  removeOnMessage(callback: MessageCallback): void {
    this.messageCallbacks = this.messageCallbacks.filter(cb => cb !== callback);
  }

  /**
   * Remove status subscription
   */
  removeOnStatusChange(callback: ConnectionStatusCallback): void {
    this.statusCallbacks = this.statusCallbacks.filter(cb => cb !== callback);
  }

  /**
   * Notify all subscribers of a new message
   */
  private notifyMessage(message: Message): void {
    this.messageCallbacks.forEach(callback => callback(message));
  }

  /**
   * Notify all subscribers of a status change
   */
  private notifyStatusChange(status: 'connected' | 'disconnected' | 'connecting'): void {
    this.statusCallbacks.forEach(callback => callback(status));
  }

  /**
   * Handle reconnection attempts
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.sessionId) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

      setTimeout(() => {
        this.connect(this.sessionId!);
      }, this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached. Please refresh the page.');
      this.notifyStatusChange('disconnected');
    }
  }

  /**
   * Simulate receiving a message (in a real implementation, this would come from WebSocket)
   */
  simulateReceiveMessage(message: Message): void {
    this.notifyMessage(message);
  }
}

export const realTimeService = new RealTimeService();
export default RealTimeService;