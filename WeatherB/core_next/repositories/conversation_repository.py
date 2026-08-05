# core_next/repositories/conversation_repository.py

from django.utils import timezone

from core_next.models import (
    AnalysisRecord,
    ConversationSession,
    ChatMessage
)

from .base_repository import BaseRepository


class ConversationRepository(BaseRepository):
    """
    Handles ConversationSession and ChatMessage persistence.
    """

    @staticmethod
    def create_session(analysis: AnalysisRecord):

        return ConversationSession.objects.create(
            analysis=analysis
        )

    @staticmethod
    def get_active_session(session_id):

        return (
            ConversationSession.objects
            .filter(
                id=session_id,
                is_active=True,
                expires_at__gt=timezone.now()
            )
            .first()
        )

    @staticmethod
    def update_last_active(session: ConversationSession):

        session.last_active = timezone.now()
        session.save(update_fields=["last_active"])

        return session

    @staticmethod
    def expire_session(session: ConversationSession):

        session.is_active = False
        session.save(update_fields=["is_active"])

        return session

    @staticmethod
    def delete_expired_sessions():

        expired = ConversationSession.objects.filter(
            expires_at__lte=timezone.now()
        )

        count = expired.count()

        expired.delete()

        return count

    @staticmethod
    def save_message(
        conversation: ConversationSession,
        role: str,
        content: str
    ):

        return ChatMessage.objects.create(
            conversation=conversation,
            role=role,
            content=content
        )

    @staticmethod
    def get_messages(conversation: ConversationSession):

        return (
            ChatMessage.objects
            .filter(conversation=conversation)
            .order_by("created_at")
        )

    @staticmethod
    def get_last_n_messages(
        conversation: ConversationSession,
        limit=10
    ):

        messages = (
            ChatMessage.objects
            .filter(conversation=conversation)
            .order_by("-created_at")[:limit]
        )

        return reversed(messages)