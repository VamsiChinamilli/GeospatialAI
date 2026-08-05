"""
chat.py

DRF serializers for chat and conversation APIs.

Responsibilities
----------------
- Serialize ConversationSession data.
- Serialize ChatMessage data.
- Validate incoming chat requests.
- Define API-facing chat response structures.

This module does NOT:
- Query the database directly.
- Run the LLM.
- Build prompts.
- Manage conversation lifecycle.
- Handle WebSocket connections.
- Perform climate analysis.
"""
from core_next.schemas.analysis import AnalysisRecordSchema
from rest_framework import serializers

from core_next.models import (
    ConversationSession,
    ChatMessage,
)


# ============================================================
# Chat Message
# ============================================================

class ChatMessageSchema(
    serializers.ModelSerializer
):
    """
    Serialize an individual chat message.
    """

    class Meta:

        model = ChatMessage

        fields = (
            "id",
            "role",
            "content",
            "created_at",
        )

        read_only_fields = (
            "id",
            "role",
            "created_at",
        )


# ============================================================
# Conversation Session
# ============================================================

class ConversationSessionSchema(
    serializers.ModelSerializer
):
    """
    Serialize a conversation session together
    with its message history.
    """
    analysis = AnalysisRecordSchema(
        read_only=True
    )
    messages = ChatMessageSchema(
        many=True,
        read_only=True,
    )

    class Meta:

        model = ConversationSession

        fields = (
            "id",
            "analysis",
            "request_type",
            "is_first_question",
            "created_at",
            "last_active",
            "expires_at",
            "is_active",
            "messages",
        )

        read_only_fields = (
            "id",
            "request_type",
            "is_first_question",
            "created_at",
            "last_active",
            "expires_at",
            "is_active",
            "messages",
        )


# ============================================================
# Chat Request
# ============================================================

class ChatRequestSchema(
    serializers.Serializer
):
    """
    Validate an incoming chat request.

    Expected:

    {
        "session_id": "uuid",
        "message": "Why is this area warm?"
    }
    """

    session_id = serializers.UUIDField(
        required=True,
    )

    message = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=5000,
    )


# ============================================================
# Chat Response
# ============================================================

class ChatResponseSchema(
    serializers.Serializer
):
    """
    Validate the structure returned after
    processing a chat question.
    """

    session_id = serializers.UUIDField(
        read_only=True,
    )

    message_id = serializers.UUIDField(
        read_only=True,
    )

    role = serializers.CharField(
        read_only=True,
    )

    content = serializers.CharField(
        read_only=True,
    )

    created_at = serializers.DateTimeField(
        read_only=True,
    )