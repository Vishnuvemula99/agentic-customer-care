"use client";

import { Bot, Plus, PanelLeftClose, PanelLeft } from "lucide-react";
import { cn } from "@/lib/utils";

interface HeaderProps {
  onNewChat: () => void;
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export function Header({ onNewChat, sidebarOpen, onToggleSidebar }: HeaderProps) {
  return (
    <header className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-4 shrink-0">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-500"
          title={sidebarOpen ? "Close sidebar" : "Open sidebar"}
        >
          {sidebarOpen ? (
            <PanelLeftClose className="w-5 h-5" />
          ) : (
            <PanelLeft className="w-5 h-5" />
          )}
        </button>

        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <h1 className="text-lg font-semibold text-gray-800">
            Customer Care <span className="text-indigo-600">AI</span>
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-400 hidden sm:block">
          Multi-Agent System
        </span>
        <button
          onClick={onNewChat}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium",
            "bg-indigo-600 text-white hover:bg-indigo-700",
            "transition-colors shadow-sm"
          )}
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>
    </header>
  );
}
