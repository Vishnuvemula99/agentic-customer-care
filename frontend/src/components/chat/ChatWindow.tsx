"use client";

import { useEffect, useRef } from "react";
import type { Message } from "@/lib/types";
import { MessageBubble } from "./MessageBubble";
import { MessageInput } from "./MessageInput";
import { TypingIndicator } from "./TypingIndicator";
import { Bot, Sparkles } from "lucide-react";

interface ChatWindowProps {
  messages: Message[];
  isStreaming: boolean;
  currentAgent: string | null;
  error: string | null;
  onSend: (message: string) => void;
}

const SAMPLE_QUERIES = [
  "What wireless headphones do you have?",
  "Where is my order ORD-2025-00001?",
  "I want to return the headphones from order ORD-2025-00001",
  "What's your return policy for electronics?",
];

export function ChatWindow({
  messages,
  isStreaming,
  currentAgent,
  error,
  onSend,
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const shouldAutoScroll = useRef(true);

  // Auto-scroll on new messages
  useEffect(() => {
    if (shouldAutoScroll.current) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isStreaming]);

  // Detect if user scrolled up
  const handleScroll = () => {
    const container = containerRef.current;
    if (!container) return;
    const { scrollTop, scrollHeight, clientHeight } = container;
    shouldAutoScroll.current = scrollHeight - scrollTop - clientHeight < 100;
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-4 py-6 scroll-smooth"
      >
        {messages.length === 0 ? (
          <EmptyState onSend={onSend} />
        ) : (
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {/* Typing indicator when streaming but no content yet */}
            {isStreaming &&
              messages.length > 0 &&
              messages[messages.length - 1].role === "assistant" &&
              messages[messages.length - 1].content === "" && (
                <div className="pl-11">
                  <TypingIndicator agent={currentAgent} />
                </div>
              )}

            {/* Error message */}
            {error && (
              <div className="max-w-3xl mx-auto px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <MessageInput onSend={onSend} disabled={isStreaming} />
    </div>
  );
}

function EmptyState({ onSend }: { onSend: (msg: string) => void }) {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center px-4">
      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mb-6 shadow-lg">
        <Bot className="w-8 h-8 text-white" />
      </div>

      <h2 className="text-2xl font-semibold text-gray-800 mb-2">
        Customer Care AI
      </h2>
      <p className="text-gray-500 mb-8 max-w-md">
        I can help you with product questions, order tracking, returns, and more.
        Powered by a multi-agent AI system.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
        {SAMPLE_QUERIES.map((query) => (
          <button
            key={query}
            onClick={() => onSend(query)}
            className="flex items-start gap-2 text-left px-4 py-3 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 hover:border-indigo-300 transition-all text-sm text-gray-600 hover:text-gray-800 shadow-sm hover:shadow"
          >
            <Sparkles className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            <span>{query}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
