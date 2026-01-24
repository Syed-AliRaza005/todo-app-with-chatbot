'use client';

import { ChatInterface } from '@/components/ChatInterface';

export default function ChatPage() {
  return (
    <div className="h-screen flex flex-col">
      <ChatInterface isWidget={false} />
    </div>
  );
}