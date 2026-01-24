import { useState } from 'react';
import { MessageCircle, X, Bot } from 'lucide-react';
import { ChatInterface } from './ChatInterface';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Chat Widget Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-blue-500 hover:bg-blue-600 text-white p-4 rounded-full shadow-lg z-50 transition-all duration-300 hover:scale-105"
          aria-label="Open chat"
        >
          <MessageCircle className="w-6 h-6" />
          <span className="absolute -top-1 -right-1 flex h-4 w-4">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-green-500"></span>
          </span>
        </button>
      )}

      {/* Chat Widget Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-lg shadow-xl z-50 border border-gray-200 flex flex-col max-h-[80vh]">
          {/* Chat Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
            <div className="flex items-center space-x-2">
              <Bot className="w-5 h-5 text-blue-500" />
              <h3 className="font-semibold text-gray-800">Chat Assistant</h3>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-full hover:bg-gray-200 transition-colors"
              aria-label="Close chat"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          {/* Chat Interface */}
          <div className="flex-1 overflow-hidden">
            <ChatInterface isWidget={true} />
          </div>
        </div>
      )}
    </>
  );
}