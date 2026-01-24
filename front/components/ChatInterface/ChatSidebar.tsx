import { ChatSession } from '@/types/session';
import { PlusCircle, MessageSquare } from 'lucide-react';

interface ChatSidebarProps {
  sessions: ChatSession[];
  activeSession: ChatSession | null;
  onSessionChange: (sessionId: string) => void;
  onNewSession: () => void;
  unreadCount: number;
}

export const ChatSidebar = ({
  sessions,
  activeSession,
  onSessionChange,
  onNewSession,
  unreadCount
}: ChatSidebarProps) => {
  return (
    <div className="flex flex-col h-full">
      {/* Sidebar Header */}
      <div className="border-b border-gray-200 bg-gray-50 p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">Chats</h2>
          <button
            onClick={onNewSession}
            className="p-2 rounded-full hover:bg-gray-200 transition-colors"
            aria-label="New chat"
          >
            <PlusCircle className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {unreadCount > 0 && (
          <div className="mt-2 text-sm text-blue-600 flex items-center">
            <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-blue-500 rounded-full mr-1">
              {unreadCount}
            </span>
            unread messages
          </div>
        )}
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto p-2">
        {sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 p-4">
            <MessageSquare className="w-12 h-12 text-gray-300 mb-2" />
            <p className="text-sm">No chat sessions yet</p>
            <button
              onClick={onNewSession}
              className="mt-3 text-sm text-blue-500 hover:text-blue-700"
            >
              Start a new conversation
            </button>
          </div>
        ) : (
          <div className="space-y-1">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => onSessionChange(session.id)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  activeSession?.id === session.id
                    ? 'bg-blue-100 border border-blue-200'
                    : 'hover:bg-gray-100'
                }`}
              >
                <div className="font-medium text-gray-800 truncate">
                  {session.title}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {session.updatedAt.toLocaleDateString()}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};