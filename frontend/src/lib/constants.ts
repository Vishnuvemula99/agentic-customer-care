export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

export const DEFAULT_USER_ID = 1;

export const AGENT_DISPLAY_NAMES: Record<string, string> = {
  product: "Product Specialist",
  order: "Order Tracker",
  returns: "Returns Specialist",
  escalation: "Escalation Handler",
  router: "Customer Care",
  system: "System",
};

export const AGENT_COLORS: Record<string, string> = {
  product: "bg-blue-100 text-blue-700 border-blue-200",
  order: "bg-emerald-100 text-emerald-700 border-emerald-200",
  returns: "bg-amber-100 text-amber-700 border-amber-200",
  escalation: "bg-red-100 text-red-700 border-red-200",
  router: "bg-purple-100 text-purple-700 border-purple-200",
  system: "bg-gray-100 text-gray-700 border-gray-200",
};

export const AGENT_ICONS: Record<string, string> = {
  product: "Package",
  order: "Truck",
  returns: "RotateCcw",
  escalation: "AlertTriangle",
  router: "Bot",
  system: "Settings",
};
