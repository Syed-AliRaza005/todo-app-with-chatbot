import { Message } from '@/types/message';
import { ChatSession } from '@/types/session';
import { MessageBubble } from './MessageBubble';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  activeSession: ChatSession | null;
}

export const ChatWindow = ({ messages, isLoading, activeSession }: ChatWindowProps) => {
  return (
    <div className="h-full flex flex-col">
      {/* Chat header */}
      <div className="border-b border-gray-200 bg-gray-50 p-4">
        <h1 className="text-xl font-semibold text-gray-800">
          {activeSession ? activeSession.title : 'Select a chat'}
        </h1>
      </div>

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <div className="text-lg mb-2">No messages yet</div>
            <div className="text-sm">Send a message to start the conversation</div>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
            />
          ))
        )}

        {isLoading && messages.length > 0 && (
          <div className="flex items-center space-x-2 p-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            <span className="text-sm text-gray-500">Thinking...</span>
          </div>
        )}
      </div>
    </div>
  );
};