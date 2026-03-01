"use client";

import {
  Bot,
  Package,
  Truck,
  RotateCcw,
  AlertTriangle,
  Settings,
} from "lucide-react";
import { AGENT_COLORS, AGENT_DISPLAY_NAMES } from "@/lib/constants";
import { cn } from "@/lib/utils";

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  product: Package,
  order: Truck,
  returns: RotateCcw,
  escalation: AlertTriangle,
  router: Bot,
  system: Settings,
};

interface AgentBadgeProps {
  agent: string;
  className?: string;
}

export function AgentBadge({ agent, className }: AgentBadgeProps) {
  const Icon = iconMap[agent] || Bot;
  const displayName = AGENT_DISPLAY_NAMES[agent] || "Assistant";
  const colorClass = AGENT_COLORS[agent] || AGENT_COLORS.system;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border",
        colorClass,
        className
      )}
    >
      <Icon className="w-3 h-3" />
      {displayName}
    </span>
  );
}
