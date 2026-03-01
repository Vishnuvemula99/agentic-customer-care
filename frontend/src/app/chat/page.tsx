"use client";

import { useCallback, useState } from "react";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { useChat } from "@/hooks/useChat";
import { getConversationMessages } from "@/lib/api";

export default function ChatPage() {
  const {
    messages,
    isStreaming,
    currentAgent,
    threadId,
    error,
    sendMessage,
    newConversation,
    loadConversation,
  } = useChat();

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleNewChat = useCallback(() => {
    newConversation();
    setRefreshTrigger((prev) => prev + 1);
  }, [newConversation]);

  const handleSelectConversation = useCallback(
    async (convThreadId: string) => {
      const msgs = await getConversationMessages(convThreadId);
      loadConversation(convThreadId, msgs);
    },
    [loadConversation]
  );

  const handleSend = useCallback(
    (content: string) => {
      sendMessage(content);
      // Refresh sidebar after a delay to show new conversation
      setTimeout(() => setRefreshTrigger((prev) => prev + 1), 1000);
    },
    [sendMessage]
  );

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        activeThreadId={threadId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        refreshTrigger={refreshTrigger}
      />

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          onNewChat={handleNewChat}
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
        />
        <main className="flex-1 overflow-hidden bg-gray-50">
          <ChatWindow
            messages={messages}
            isStreaming={isStreaming}
            currentAgent={currentAgent}
            error={error}
            onSend={handleSend}
          />
        </main>
      </div>
    </div>
  );
}
