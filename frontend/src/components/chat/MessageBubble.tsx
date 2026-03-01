"use client";

import type { Message } from "@/lib/types";
import { cn, formatTimestamp } from "@/lib/utils";
import { AgentBadge } from "./AgentBadge";
import { MarkdownRenderer } from "./MarkdownRenderer";
import { User } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1",
          isUser
            ? "bg-indigo-600 text-white"
            : "bg-gradient-to-br from-emerald-400 to-cyan-500 text-white"
        )}
      >
        {isUser ? (
          <User className="w-4 h-4" />
        ) : (
          <span className="text-sm font-bold">AI</span>
        )}
      </div>

      {/* Message content */}
      <div
        className={cn("max-w-[75%] space-y-1", isUser ? "items-end" : "items-start")}
      >
        {/* Agent badge for assistant messages */}
        {!isUser && message.agent && (
          <div className={cn(isUser ? "flex justify-end" : "flex justify-start")}>
            <AgentBadge agent={message.agent} />
          </div>
        )}

        {/* Bubble */}
        <div
          className={cn(
            "rounded-2xl px-4 py-2.5 text-sm leading-relaxed break-words",
            isUser
              ? "bg-indigo-600 text-white rounded-br-md whitespace-pre-wrap"
              : "bg-white text-gray-800 border border-gray-200 rounded-bl-md shadow-sm"
          )}
        >
          {isUser ? (
            message.content
          ) : (
            <MarkdownRenderer content={message.content} />
          )}
        </div>

        {/* Timestamp */}
        <p
          className={cn(
            "text-[10px] text-gray-400 px-1",
            isUser ? "text-right" : "text-left"
          )}
        >
          {formatTimestamp(message.timestamp)}
        </p>
      </div>
    </div>
  );
}
