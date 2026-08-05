"""
consumers.py

WebSocket consumer for the Urban Climate Copilot.

Responsibilities
----------------
- Accept WebSocket connections.
- Validate incoming WebSocket messages.
- Load conversation sessions.
- Connect WebSocket requests to ConversationService.
- Stream LLM response chunks to the frontend.
- Send lifecycle events to the frontend.

This consumer does NOT:
- Build LLM prompts.
- Communicate directly with Ollama.
- Perform raster processing.
- Run ML models.
- Calculate LST.
- Implement conversation business logic.
"""

import asyncio
import traceback

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from core_next.models import ConversationSession

from core_next.services.conversation.conversation_service import (
    ConversationService,
)

from core_next.services.llm.llm_service import (
    LLMService,
)

from core_next.services.llm.provider_manager import (
    ProviderManager,
)


class UrbanCopilotConsumer(
    AsyncJsonWebsocketConsumer
):
    """
    WebSocket consumer for conversational
    urban climate analysis.
    """

    # ============================================================
    # Connection
    # ============================================================

    async def connect(self):
        """
        Accept the WebSocket connection.
        """

        self.session_id = (
            self.scope["url_route"]["kwargs"].get(
                "session_id"
            )
        )

        if not self.session_id:

            await self.close(
                code=4000
            )

            return

        await self.accept()

        await self.send_json(
            {
                "type": "connection",
                "status": "connected",
                "session_id": str(
                    self.session_id
                ),
            }
        )

    # ============================================================
    # Disconnect
    # ============================================================

    async def disconnect(
        self,
        close_code
    ):
        """
        Handle WebSocket disconnection.
        """

        return

    # ============================================================
    # Receive
    # ============================================================

    async def receive_json(
        self,
        content
    ):
        """
        Receive a JSON message from the frontend.

        Expected:

        {
            "message": "Why is this area warm?"
        }
        """

        # --------------------------------------------------------
        # Validate JSON object
        # --------------------------------------------------------

        if not isinstance(
            content,
            dict
        ):

            await self.send_json(
                {
                    "type": "error",
                    "message":
                        "WebSocket message must be a JSON object.",
                }
            )

            return

        # --------------------------------------------------------
        # Extract message
        # --------------------------------------------------------

        user_message = content.get(
            "message"
        )

        if not isinstance(
            user_message,
            str
        ):

            await self.send_json(
                {
                    "type": "error",
                    "message":
                        "Message must be a string.",
                }
            )

            return

        user_message = user_message.strip()

        if not user_message:

            await self.send_json(
                {
                    "type": "error",
                    "message":
                        "Message cannot be empty.",
                }
            )

            return

        if len(user_message) > 5000:

            await self.send_json(
                {
                    "type": "error",
                    "message":
                        "Message cannot exceed 5000 characters.",
                }
            )

            return

        # --------------------------------------------------------
        # Tell frontend that generation started
        # --------------------------------------------------------

        await self.send_json(
            {
                "type": "response_start",
            }
        )

        try:

            # ----------------------------------------------------
            # Load conversation session
            # ----------------------------------------------------

            session = await self.get_session()

            # ----------------------------------------------------
            # Build conversation service
            # ----------------------------------------------------

            conversation_service = (
                self.get_conversation_service()
            )

            # ----------------------------------------------------
            # Stream response
            #
            # ConversationService is synchronous.
            #
            # Therefore stream_from_service() creates a worker
            # thread and safely forwards chunks back to this
            # asynchronous WebSocket consumer.
            # ----------------------------------------------------

            full_response = []

            async for chunk in self.stream_from_service(
                conversation_service=conversation_service,
                session=session,
                user_message=user_message,
            ):

                full_response.append(
                    chunk
                )

                await self.send_json(
                    {
                        "type": "token",
                        "content": chunk,
                    }
                )

            # ----------------------------------------------------
            # Complete response
            # ----------------------------------------------------

            complete_response = "".join(
                full_response
            )

            await self.send_json(
                {
                    "type": "response_end",
                    "content": complete_response,
                }
            )

        except ValueError as exc:

            await self.send_json(
                {
                    "type": "error",
                    "message": str(exc),
                }
            )

        except RuntimeError as exc:

            await self.send_json(
                {
                    "type": "error",
                    "message": str(exc),
                }
            )

        except Exception as exc:

            traceback.print_exc()

            await self.send_json(
                {
                    "type": "error",
                    "message":
                        "An unexpected server error occurred.",
                }
            )

    # ============================================================
    # Streaming Bridge
    # ============================================================

    async def stream_from_service(
        self,
        conversation_service,
        session,
        user_message,
    ):
        """
        Bridge the synchronous ConversationService streaming
        generator into the asynchronous WebSocket consumer.

        Architecture:

            Async WebSocket
                    ↓
              Worker thread
                    ↓
          ConversationService
                    ↓
            Django ORM + Ollama
                    ↓
              asyncio.Queue
                    ↓
            Async WebSocket
        """

        queue = asyncio.Queue()

        loop = asyncio.get_running_loop()

        # --------------------------------------------------------
        # Synchronous producer
        # --------------------------------------------------------

        def producer():
            """
            Run the synchronous conversation pipeline
            inside a worker thread.
            """

            try:

                for chunk in (
                    conversation_service.process_question_stream(
                        session=session,
                        user_question=user_message,
                    )
                ):

                    loop.call_soon_threadsafe(
                        queue.put_nowait,
                        (
                            "chunk",
                            chunk,
                        ),
                    )

                # Signal completion

                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    (
                        "done",
                        None,
                    ),
                )

            except Exception as exc:

                # Forward exception to async side

                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    (
                        "error",
                        exc,
                    ),
                )

        # --------------------------------------------------------
        # Start worker thread
        # --------------------------------------------------------

        worker_task = asyncio.create_task(
            asyncio.to_thread(
                producer
            )
        )

        # --------------------------------------------------------
        # Consume queue
        # --------------------------------------------------------

        try:

            while True:

                event_type, value = (
                    await queue.get()
                )

                # ----------------------------------------------
                # Token
                # ----------------------------------------------

                if event_type == "chunk":

                    yield value

                    continue

                # ----------------------------------------------
                # Error
                # ----------------------------------------------

                if event_type == "error":

                    raise value

                # ----------------------------------------------
                # Finished
                # ----------------------------------------------

                if event_type == "done":

                    break

        finally:

            # Ensure producer finishes cleanly

            await worker_task

    # ============================================================
    # Session
    # ============================================================

    @database_sync_to_async
    def get_session(self):
        """
        Retrieve the conversation session safely
        from the Django ORM.
        """

        try:

            return ConversationSession.objects.get(
                id=self.session_id
            )

        except ConversationSession.DoesNotExist as exc:

            raise ValueError(
                "Conversation session does not exist."
            ) from exc

    # ============================================================
    # Conversation Service
    # ============================================================

    @staticmethod
    def get_conversation_service():
        """
        Construct the conversation service with
        the configured LLM service.

        This is temporary dependency wiring.

        Later this can move into a dedicated
        application/service factory.
        """

        provider = ProviderManager()

        llm_service = LLMService(
            provider=provider
        )

        return ConversationService(
            llm_service=llm_service
        )