from __future__ import annotations

"""Chat endpoints — send messages and receive responses from the agent system."""

import asyncio
import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.graph import invoke_graph, stream_graph
from app.guardrails.input_validator import sanitize_input, validate_input
from app.guardrails.output_validator import validate_output
from app.memory.conversation_store import (
    create_conversation,
    get_conversation,
    update_conversation,
)
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest) -> ChatMessageResponse:
    """Send a message and receive a complete response.

    If thread_id is not provided, a new conversation is created.
    Applies input validation, agent processing, and output validation.
    """
    # --- Input guardrail ---
    is_valid, rejection_reason = validate_input(request.message)
    if not is_valid:
        thread_id = request.thread_id or create_conversation(request.user_id)
        return ChatMessageResponse(
            response=rejection_reason or "Invalid message.",
            thread_id=thread_id,
            agent="system",
            escalated=False,
            intent="blocked",
        )

    sanitized_message = sanitize_input(request.message)

    # Create or validate conversation
    thread_id = request.thread_id
    if not thread_id:
        thread_id = create_conversation(request.user_id)
        logger.info(f"Created new conversation: {thread_id}")

    # Invoke the agent graph
    logger.info(f"[CHAT] Invoking graph: message='{sanitized_message[:80]}...', thread={thread_id}, user={request.user_id}")
    result = await asyncio.to_thread(
        invoke_graph,
        message=sanitized_message,
        thread_id=thread_id,
        user_id=request.user_id,
    )
    logger.info(f"[CHAT] Graph result: agent={result.get('agent')}, response_len={len(result.get('response', ''))}, escalated={result.get('escalated')}")
    logger.info(f"[CHAT] Graph response preview: {result.get('response', '')[:300]}")

    # --- Output guardrail ---
    validated_response, warnings = validate_output(
        result["response"], result.get("agent", "router")
    )
    for warning in warnings:
        logger.warning(f"Output guardrail: {warning}")

    logger.info(f"[CHAT] Validated response length: {len(validated_response)}")

    # Update conversation metadata
    update_conversation(
        thread_id=thread_id,
        preview=request.message,
        agent=result.get("agent", ""),
    )

    resp = ChatMessageResponse(
        response=validated_response,
        thread_id=thread_id,
        agent=result.get("agent", "router"),
        escalated=result.get("escalated", False),
        intent=result.get("intent", ""),
    )
    logger.info(f"[CHAT] Returning: {resp.model_dump_json()[:500]}")
    return resp


@router.post("/stream")
async def stream_message(request: ChatMessageRequest):
    """Send a message and receive a streaming response via Server-Sent Events (SSE).

    Events:
    - event: metadata / data: {"agent": "product"}
    - event: token / data: {"token": "Hello"}
    - event: done / data: {"thread_id": "...", "agent": "..."}
    - event: error / data: {"message": "..."}
    """
    # --- Input guardrail ---
    is_valid, rejection_reason = validate_input(request.message)
    if not is_valid:
        thread_id = request.thread_id or create_conversation(request.user_id)

        async def blocked_response():
            msg = rejection_reason or "Invalid message."
            yield f"event: metadata\ndata: {json.dumps({'agent': 'system'})}\n\n"
            yield f"event: token\ndata: {json.dumps({'token': msg})}\n\n"
            yield f"event: done\ndata: {json.dumps({'thread_id': thread_id, 'agent': 'system'})}\n\n"

        return StreamingResponse(
            blocked_response(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
        )

    sanitized_message = sanitize_input(request.message)

    thread_id = request.thread_id
    if not thread_id:
        thread_id = create_conversation(request.user_id)

    async def event_generator():
        """Generate SSE events from the agent graph stream."""
        try:
            async for event in stream_graph(
                message=sanitized_message,
                thread_id=thread_id,
                user_id=request.user_id,
            ):
                event_type = event.get("event", "token")
                event_data = json.dumps(event.get("data", {}))
                yield f"event: {event_type}\ndata: {event_data}\n\n"

                # Update conversation on completion
                if event_type == "done":
                    agent = event.get("data", {}).get("agent", "")
                    update_conversation(
                        thread_id=thread_id,
                        preview=request.message,
                        agent=agent,
                    )

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            error_data = json.dumps({"message": "An error occurred during streaming"})
            yield f"event: error\ndata: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
