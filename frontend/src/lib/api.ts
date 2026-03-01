import { API_BASE_URL } from "./constants";
import type { ChatRequest, ChatResponse, Conversation, Message } from "./types";

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/api/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function streamMessage(
  request: ChatRequest,
  onToken: (token: string) => void,
  onMetadata: (meta: { agent: string }) => void,
  onDone: (data: { thread_id: string; agent: string }) => void,
  onError: (error: string) => void,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      let eventType = "";
      for (const line of lines) {
        if (line.startsWith("event:")) {
          eventType = line.slice(6).trim();
        } else if (line.startsWith("data:")) {
          const dataStr = line.slice(5).trim();
          if (!dataStr) continue;

          try {
            const data = JSON.parse(dataStr);

            switch (eventType) {
              case "token":
                onToken(data.token);
                break;
              case "metadata":
                onMetadata(data);
                break;
              case "done":
                onDone(data);
                break;
              case "error":
                onError(data.message);
                break;
            }
          } catch {
            // Skip malformed JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export async function getConversations(userId: number): Promise<Conversation[]> {
  const res = await fetch(`${API_BASE_URL}/api/conversations/${userId}`);
  if (!res.ok) return [];
  return res.json();
}

export async function getConversationMessages(threadId: string): Promise<Message[]> {
  const res = await fetch(`${API_BASE_URL}/api/conversations/${threadId}/messages`);
  if (!res.ok) return [];
  return res.json();
}

export async function deleteConversation(threadId: string): Promise<void> {
  await fetch(`${API_BASE_URL}/api/conversations/${threadId}`, {
    method: "DELETE",
  });
}
