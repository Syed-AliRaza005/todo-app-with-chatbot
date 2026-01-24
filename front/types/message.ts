export interface Message {
  id: string;
  sessionId: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status: 'sent' | 'delivered' | 'read' | 'failed';
}