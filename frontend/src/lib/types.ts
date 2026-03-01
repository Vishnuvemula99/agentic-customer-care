export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  agent?: string;
  timestamp: string;
}

export interface Conversation {
  thread_id: string;
  created_at: string;
  preview: string;
  message_count: number;
  last_agent?: string;
}

export interface ChatRequest {
  message: string;
  thread_id?: string | null;
  user_id: number;
}

export interface ChatResponse {
  response: string;
  thread_id: string;
  agent: string;
  escalated: boolean;
  intent: string;
}

export interface StreamEvent {
  event: "token" | "metadata" | "done" | "error";
  data: Record<string, unknown>;
}
