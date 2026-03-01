"use client";

import { useEffect, useState } from "react";
import { MessageSquare, Trash2, Plus } from "lucide-react";
import type { Conversation } from "@/lib/types";
import { getConversations, deleteConversation as apiDeleteConversation } from "@/lib/api";
import { DEFAULT_USER_ID } from "@/lib/constants";
import { cn, formatTimestamp } from "@/lib/utils";

interface SidebarProps {
  isOpen: boolean;
  activeThreadId: string | null;
  onSelectConversation: (threadId: string) => void;
  onNewChat: () => void;
  refreshTrigger: number;
}

export function Sidebar({
  isOpen,
  activeThreadId,
  onSelectConversation,
  onNewChat,
  refreshTrigger,
}: SidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    getConversations(DEFAULT_USER_ID).then(setConversations);
  }, [refreshTrigger]);

  const handleDelete = async (e: React.MouseEvent, threadId: string) => {
    e.stopPropagation();
    await apiDeleteConversation(threadId);
    setConversations((prev) => prev.filter((c) => c.thread_id !== threadId));
  };

  return (
    <div
      className={cn(
        "h-full bg-gray-50 border-r border-gray-200 flex flex-col transition-all duration-300",
        isOpen ? "w-72" : "w-0 overflow-hidden"
      )}
    >
      {/* New chat button */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 text-sm text-gray-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New conversation
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-2 pb-4">
        {conversations.length === 0 ? (
          <p className="text-xs text-gray-400 text-center mt-8 px-4">
            No conversations yet. Start chatting!
          </p>
        ) : (
          <div className="space-y-1">
            {conversations.map((conv) => (
              <button
                key={conv.thread_id}
                onClick={() => onSelectConversation(conv.thread_id)}
                className={cn(
                  "w-full text-left px-3 py-2.5 rounded-lg group transition-colors flex items-start gap-2",
                  activeThreadId === conv.thread_id
                    ? "bg-indigo-50 border border-indigo-200"
                    : "hover:bg-gray-100"
                )}
              >
                <MessageSquare className="w-4 h-4 text-gray-400 shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 truncate">
                    {conv.preview || "New conversation"}
                  </p>
                  <p className="text-[10px] text-gray-400 mt-0.5">
                    {formatTimestamp(conv.created_at)} &middot;{" "}
                    {conv.message_count} messages
                  </p>
                </div>
                <div
                  role="button"
                  tabIndex={0}
                  onClick={(e) => handleDelete(e, conv.thread_id)}
                  onKeyDown={(e) => { if (e.key === "Enter") handleDelete(e as unknown as React.MouseEvent, conv.thread_id); }}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-50 hover:text-red-500 text-gray-400 transition-all cursor-pointer"
                  title="Delete conversation"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-gray-200">
        <div className="flex items-center gap-2 px-2">
          <div className="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center">
            <span className="text-[10px] font-bold text-indigo-600">AJ</span>
          </div>
          <div className="text-xs">
            <p className="text-gray-700 font-medium">Alice Johnson</p>
            <p className="text-gray-400">Premium Member</p>
          </div>
        </div>
      </div>
    </div>
  );
}
