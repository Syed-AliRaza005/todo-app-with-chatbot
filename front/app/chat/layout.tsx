'use client';

import { ReactNode } from 'react';
import { usePathname } from 'next/navigation';

interface ChatLayoutProps {
  children: ReactNode;
}

export default function ChatLayout({ children }: ChatLayoutProps) {
  const pathname = usePathname();

  return (
    <div className="h-screen flex flex-col">
      {children}
    </div>
  );
}