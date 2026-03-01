"use client";

import { useCallback, useRef, useState } from "react";
import { sendMessage } from "@/lib/api";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type { Message } from "@/lib/types";
import { generateId } from "@/lib/utils";

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendUserMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      setError(null);

      // Add user message immediately (optimistic)
      const userMsg: Message = {
        id: generateId(),
        role: "user",
        content: content.trim(),
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsLoading(true);
      setCurrentAgent(null);

      // Create a placeholder assistant message (shows typing indicator)
      const assistantMsgId = generateId();
      const assistantMsg: Message = {
        id: assistantMsgId,
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      try {
        console.log("[useChat] Sending message via /message endpoint...");
        const response = await sendMessage({
          message: content.trim(),
          thread_id: threadId,
          user_id: DEFAULT_USER_ID,
        });
        console.log("[useChat] Response received:", {
          agent: response.agent,
          intent: response.intent,
          responseLen: response.response?.length,
          threadId: response.thread_id,
        });

        // Update the placeholder assistant message with the actual response
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMsgId
              ? {
                  ...msg,
                  content: response.response,
                  agent: response.agent,
                }
              : msg
          )
        );
        setThreadId(response.thread_id);
        setCurrentAgent(response.agent);
      } catch (err) {
        console.error("[useChat] Request failed:", (err as Error).message);
        setError((err as Error).message);
        // Remove the empty placeholder on error
        setMessages((prev) =>
          prev.filter((msg) => msg.id !== assistantMsgId)
        );
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, threadId]
  );

  const newConversation = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
    setMessages([]);
    setThreadId(null);
    setCurrentAgent(null);
    setError(null);
    setIsLoading(false);
  }, []);

  const loadConversation = useCallback(
    (convThreadId: string, convMessages: Message[]) => {
      if (abortRef.current) abortRef.current.abort();
      setThreadId(convThreadId);
      setMessages(convMessages);
      setCurrentAgent(null);
      setError(null);
      setIsLoading(false);
    },
    []
  );

  return {
    messages,
    isStreaming: isLoading,
    currentAgent,
    threadId,
    error,
    sendMessage: sendUserMessage,
    newConversation,
    loadConversation,
  };
}
