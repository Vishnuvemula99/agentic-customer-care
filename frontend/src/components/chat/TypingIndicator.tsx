"use client";

import { AGENT_DISPLAY_NAMES } from "@/lib/constants";

interface TypingIndicatorProps {
  agent?: string | null;
}

export function TypingIndicator({ agent }: TypingIndicatorProps) {
  const agentName = agent
    ? AGENT_DISPLAY_NAMES[agent] || "Assistant"
    : "Assistant";

  return (
    <div className="flex items-center gap-2 text-sm text-gray-500 px-1">
      <div className="flex gap-1">
        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
        <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
      </div>
      <span className="text-xs">{agentName} is thinking...</span>
    </div>
  );
}
