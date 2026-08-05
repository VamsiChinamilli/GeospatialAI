"""
conversation_service.py

Conversation orchestration service.

Responsibilities
----------------
- Create conversation sessions.
- Load existing conversation sessions.
- Validate session availability.
- Store user messages.
- Store assistant messages.
- Load conversation history.
- Retain only the latest three user/assistant exchanges.
- Build the context required by LLMService.
- Connect conversation persistence with the LLM layer.

This service does NOT:
- Perform climate analysis.
- Build LLM prompts.
- Communicate directly with Ollama.
- Decide scientific response rules.
- Handle HTTP requests.
- Handle WebSocket connections.
"""

from typing import Any, Dict, List, Optional

from django.db import transaction
from django.utils import timezone

from core_next.models import (
    AnalysisRecord,
    ChatMessage,
    ConversationSession,
)


class ConversationService:
    """
    Service responsible for managing conversations
    around an AnalysisRecord.
    """

    # ============================================================
    # Configuration
    # ============================================================

    MAX_EXCHANGES = 3

    MAX_HISTORY_MESSAGES = MAX_EXCHANGES * 2

    MAX_MESSAGE_LENGTH = 5000

    # ============================================================
    # Initialization
    # ============================================================

    def __init__(
        self,
        llm_service=None,
    ):
        """
        Parameters
        ----------
        llm_service:
            Optional LLMService instance.

            It is injected rather than created here so that
            the conversation service remains independent of
            a specific LLM provider.
        """

        self.llm_service = llm_service

    # ============================================================
    # Create Conversation
    # ============================================================

    @transaction.atomic
    def create_session(
        self,
        analysis: AnalysisRecord,
    ) -> ConversationSession:
        """
        Create a new conversation session for an analysis.

        A conversation belongs to exactly one analysis.
        """

        if not isinstance(
            analysis,
            AnalysisRecord,
        ):
            raise TypeError(
                "analysis must be an AnalysisRecord instance."
            )

        session = ConversationSession.objects.create(
            analysis=analysis,
            request_type="NEW_LOCATION",
            is_first_question=True,
        )

        return session

    # ============================================================
    # Get Session
    # ============================================================

    def get_session(
        self,
        session_id,
    ) -> ConversationSession:
        """
        Retrieve an active conversation session.

        Expired or inactive sessions are rejected.
        """

        try:

            session = ConversationSession.objects.get(
                id=session_id
            )

        except ConversationSession.DoesNotExist as exc:

            raise ValueError(
                "Conversation session does not exist."
            ) from exc

        self._validate_session(
            session
        )

        return session

    # ============================================================
    # Validate Session
    # ============================================================

    @staticmethod
    def _validate_session(
        session: ConversationSession,
    ) -> None:
        """
        Ensure the conversation can still be used.
        """

        if not session.is_active:

            raise ValueError(
                "Conversation session is inactive."
            )

        now = timezone.now()

        if session.expires_at <= now:

            session.is_active = False

            session.save(
                update_fields=[
                    "is_active",
                ]
            )

            raise ValueError(
                "Conversation session has expired."
            )

    # ============================================================
    # Update Activity
    # ============================================================

    @staticmethod
    def _touch_session(
        session: ConversationSession,
    ) -> None:
        """
        Update the session's activity timestamp.
        """

        session.last_active = timezone.now()

        session.save(
            update_fields=[
                "last_active",
            ]
        )

    # ============================================================
    # Save User Message
    # ============================================================

    @transaction.atomic
    def save_user_message(
        self,
        session: ConversationSession,
        content: str,
    ) -> ChatMessage:
        """
        Persist a user message.
        """

        self._validate_session(
            session
        )

        content = self._validate_message_content(
            content
        )

        message = ChatMessage.objects.create(
            conversation=session,
            role="user",
            content=content,
        )

        self._touch_session(
            session
        )

        return message

    # ============================================================
    # Save Assistant Message
    # ============================================================

    @transaction.atomic
    def save_assistant_message(
        self,
        session: ConversationSession,
        content: str,
    ) -> ChatMessage:
        """
        Persist an assistant response.
        """

        self._validate_session(
            session
        )

        content = self._validate_message_content(
            content
        )

        message = ChatMessage.objects.create(
            conversation=session,
            role="assistant",
            content=content,
        )

        self._touch_session(
            session
        )

        return message

    # ============================================================
    # Save System Message
    # ============================================================

    @transaction.atomic
    def save_system_message(
        self,
        session: ConversationSession,
        content: str,
    ) -> ChatMessage:
        """
        Persist a system message when required.

        System messages should normally be generated by
        backend logic rather than directly by the client.
        """

        self._validate_session(
            session
        )

        content = self._validate_message_content(
            content
        )

        message = ChatMessage.objects.create(
            conversation=session,
            role="system",
            content=content,
        )

        self._touch_session(
            session
        )

        return message

    # ============================================================
    # Message Validation
    # ============================================================

    @classmethod
    def _validate_message_content(
        cls,
        content: str,
    ) -> str:
        """
        Validate and normalize message text.
        """

        if not isinstance(
            content,
            str,
        ):
            raise TypeError(
                "Message content must be a string."
            )

        content = content.strip()

        if not content:

            raise ValueError(
                "Message content cannot be empty."
            )

        if len(content) > cls.MAX_MESSAGE_LENGTH:

            raise ValueError(
                "Message content cannot exceed "
                f"{cls.MAX_MESSAGE_LENGTH} characters."
            )

        return content

    # ============================================================
    # Conversation History
    # ============================================================

    def get_history(
        self,
        session: ConversationSession,
    ) -> List[Dict[str, Any]]:
        """
        Return only the latest three user/assistant exchanges.

        One exchange consists of:

            user
            assistant

        Therefore the maximum history returned is:

            3 exchanges × 2 messages = 6 messages

        System messages are excluded from conversational history.
        """

        self._validate_session(
            session
        )

        messages = list(
            session.messages
            .filter(
                role__in=[
                    "user",
                    "assistant",
                ]
            )
            .order_by(
                "-created_at"
            )[
                :self.MAX_HISTORY_MESSAGES
            ]
        )

        # We queried newest → oldest so that slicing gives us
        # the latest six messages. Reverse them before sending
        # them to the LLM so the conversation remains chronological.
        messages.reverse()

        history = []

        for message in messages:

            history.append(
                {
                    "role": message.role,
                    "content": message.content,
                }
            )

        return history

    # ============================================================
    # Build LLM Context
    # ============================================================

    def build_llm_context(
        self,
        session: ConversationSession,
        user_question: str,
        conversation_history: Optional[
            List[Dict[str, Any]]
        ] = None,
    ) -> Dict[str, Any]:
        """
        Build the structured context consumed by LLMService.

        conversation_history may be supplied explicitly when the
        caller wants to guarantee that the current user question
        is not included in previous history.
        """

        self._validate_session(
            session
        )

        user_question = self._validate_message_content(
            user_question
        )

        analysis = session.analysis

        if conversation_history is None:

            conversation_history = self.get_history(
                session
            )

        context = {

            "request_type": (
                "NEW_LOCATION"
                if session.is_first_question
                else "FOLLOW_UP"
            ),

            "user_question": user_question,

            "analysis": (
                analysis.analysis_metrics
            ),

            "conversation_history": (
                conversation_history
            ),

            "instructions": {

                "use_current_analysis": True,

                "use_conversation_history": (
                    not session.is_first_question
                ),

                "experimental_lst_unet": False,

            },

        }

        return context

    # ============================================================
    # Mark Question Completed
    # ============================================================

    @staticmethod
    def _mark_question_completed(
        session: ConversationSession,
    ) -> None:
        """
        Mark the first question as completed.

        After the first successful assistant response,
        subsequent requests become FOLLOW_UP requests.
        """

        if session.is_first_question:

            session.is_first_question = False
            session.request_type = "FOLLOW_UP"

            session.save(
                update_fields=[
                    "is_first_question",
                    "request_type",
                ]
            )

    # ============================================================
    # Process User Question
    # ============================================================

    @transaction.atomic
    def process_question(
        self,
        session: ConversationSession,
        user_question: str,
    ) -> str:
        """
        Process a user question through the complete
        conversation + LLM pipeline.

        Flow
        ----
        User question
            ↓
        Validate session
            ↓
        Load previous history
            ↓
        Save user message
            ↓
        Build LLM context
            ↓
        LLMService
            ↓
        Save assistant response
            ↓
        Update session state
            ↓
        Return response
        """

        if self.llm_service is None:

            raise RuntimeError(
                "LLMService has not been configured."
            )

        self._validate_session(
            session
        )

        user_question = self._validate_message_content(
            user_question
        )

        # --------------------------------------------------------
        # IMPORTANT:
        # Capture history BEFORE saving the current user message.
        #
        # This prevents the current question from appearing twice
        # in the LLM context.
        # --------------------------------------------------------

        previous_history = self.get_history(
            session
        )

        # --------------------------------------------------------
        # Save user message
        # --------------------------------------------------------

        self.save_user_message(
            session=session,
            content=user_question,
        )

        # --------------------------------------------------------
        # Build context
        # --------------------------------------------------------

        context = self.build_llm_context(
            session=session,
            user_question=user_question,
            conversation_history=previous_history,
        )

        # --------------------------------------------------------
        # Generate assistant response
        # --------------------------------------------------------

        response = self.llm_service.generate(
            context
        )

        if not isinstance(
            response,
            str,
        ):
            raise TypeError(
                "LLMService must return a string."
            )

        response = response.strip()

        if not response:

            raise ValueError(
                "LLMService returned an empty response."
            )

        # --------------------------------------------------------
        # Save assistant response
        # --------------------------------------------------------

        self.save_assistant_message(
            session=session,
            content=response,
        )

        # --------------------------------------------------------
        # Update session state
        # --------------------------------------------------------

        self._mark_question_completed(
            session
        )

        return response

    # ============================================================
    # Streaming Question
    # ============================================================

    def process_question_stream(
        self,
        session: ConversationSession,
        user_question: str,
    ):
        """
        Stream an assistant response through LLMService.

        The generated chunks are yielded immediately.

        The complete response is accumulated so that the
        final assistant response can be persisted after
        streaming finishes.

        The WebSocket layer will consume this generator later.
        """

        if self.llm_service is None:

            raise RuntimeError(
                "LLMService has not been configured."
            )

        self._validate_session(
            session
        )

        user_question = self._validate_message_content(
            user_question
        )

        # --------------------------------------------------------
        # Capture previous history BEFORE saving current question.
        # --------------------------------------------------------

        previous_history = self.get_history(
            session
        )

        # --------------------------------------------------------
        # Save user message
        # --------------------------------------------------------

        self.save_user_message(
            session=session,
            content=user_question,
        )

        # --------------------------------------------------------
        # Build context
        # --------------------------------------------------------

        context = self.build_llm_context(
            session=session,
            user_question=user_question,
            conversation_history=previous_history,
        )

        # --------------------------------------------------------
        # Stream response
        # --------------------------------------------------------

        chunks = []

        for chunk in self.llm_service.generate_stream(
            context
        ):

            if not isinstance(
                chunk,
                str,
            ):
                raise TypeError(
                    "LLM stream must yield strings."
                )

            if not chunk:
                continue

            chunks.append(
                chunk
            )

            yield chunk

        # --------------------------------------------------------
        # Reconstruct complete response
        # --------------------------------------------------------

        response = "".join(
            chunks
        ).strip()

        if not response:

            raise ValueError(
                "LLM stream returned an empty response."
            )

        # --------------------------------------------------------
        # Save assistant response
        # --------------------------------------------------------

        self.save_assistant_message(
            session=session,
            content=response,
        )

        # --------------------------------------------------------
        # Update session state
        # --------------------------------------------------------

        self._mark_question_completed(
            session
        )

    # ============================================================
    # End Session
    # ============================================================

    @transaction.atomic
    def close_session(
        self,
        session: ConversationSession,
    ) -> ConversationSession:
        """
        Explicitly close a conversation session.
        """

        session.is_active = False

        session.save(
            update_fields=[
                "is_active",
            ]
        )

        return session