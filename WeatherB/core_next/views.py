"""
views.py

DRF API views for the Urban Climate AI system.

Responsibilities
----------------
- Receive HTTP requests.
- Validate request data using schemas.
- Coordinate application services.
- Return serialized API responses.

This module does NOT:
- Build LLM prompts.
- Communicate directly with Ollama.
- Perform raster processing itself.
- Run ML models itself.
- Manage WebSocket connections.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core_next.models import AnalysisRecord

from core_next.schemas.analysis import (
    AnalysisCreateSchema,
    AnalysisRecordSchema,
)

from core_next.schemas.chat import (
    ChatRequestSchema,
    ChatResponseSchema,
    ConversationSessionSchema,
)

from core_next.services.conversation.conversation_service import (
    ConversationService,
)

from core_next.services.raster_service import (
    RasterService,
)

from core_next.services.ai_processing_service import (
    AIProcessingService,
)

from core_next.services.analysis_service import (
    AnalysisService,
)


# ============================================================
# Analysis View
# ============================================================

class AnalysisView(APIView):
    """
    Handle creation of a complete geospatial analysis
    and its associated conversation session.
    """

    def post(self, request):

        # ----------------------------------------------------
        # 1. Validate request
        # ----------------------------------------------------

        serializer = AnalysisCreateSchema(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        bbox = serializer.validated_data["bbox"]

        # ----------------------------------------------------
        # 2. Raster acquisition
        # ----------------------------------------------------

        try:

            raster_service = RasterService()

            climate_data = (
                raster_service.fetch_raster(
                    bbox=bbox
                )
            )

        except ValueError as exc:

            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except RuntimeError as exc:

            return Response(
                {"detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # ----------------------------------------------------
        # 3. AI processing
        # ----------------------------------------------------

        try:

            ai_processing_service = (
                AIProcessingService()
            )

            ai_result = (
                ai_processing_service.process(
                    climate_data=climate_data
                )
            )

        except ValueError as exc:

            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except RuntimeError as exc:

            return Response(
                {"detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ----------------------------------------------------
        # 4. Application-level analysis
        # ----------------------------------------------------

        try:

            analysis_service = AnalysisService()

            analysis_metrics = (
                analysis_service.analyze(
                    ai_result=ai_result
                )
            )

        except (ValueError, TypeError, KeyError) as exc:

            return Response(
                {"detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ----------------------------------------------------
        # 5. Save analysis
        # ----------------------------------------------------

        try:

            analysis = AnalysisRecord.objects.create(

                bbox=bbox,

                analysis_metrics=analysis_metrics,

                model_metadata={
                    "land_cover_model":
                        "Land-Cover U-Net",

                    "lst_method":
                        "LST Expert System",

                    "raster_provider":
                        "Google Earth Engine",

                    "llm":
                        "Not used during analysis",
                },
            )

        except Exception as exc:

            return Response(
                {
                    "detail":
                        "Failed to save analysis record.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ----------------------------------------------------
        # 6. Create conversation session
        # ----------------------------------------------------

        try:

            conversation_service = (
                ConversationService()
            )

            session = (
                conversation_service.create_session(
                    analysis=analysis
                )
            )

        except Exception as exc:

            # Analysis exists, but its conversation could
            # not be created. Remove the orphaned analysis.

            analysis.delete()

            return Response(
                {
                    "detail":
                        "Failed to create conversation session.",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ----------------------------------------------------
        # 7. Serialize response
        # ----------------------------------------------------

        response_data = {

            "analysis":
                AnalysisRecordSchema(
                    analysis
                ).data,

            "session":
                ConversationSessionSchema(
                    session
                ).data,
        }

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# Chat View
# ============================================================

class ChatView(APIView):
    """
    Handle normal non-streaming chat requests.

    Streaming will be handled separately through
    Django Channels / WebSocket consumers.
    """

    def post(self, request):

        # ----------------------------------------------------
        # 1. Validate request
        # ----------------------------------------------------

        serializer = ChatRequestSchema(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        session_id = (
            serializer.validated_data["session_id"]
        )

        message = (
            serializer.validated_data["message"]
        )

        # ----------------------------------------------------
        # 2. Create conversation service
        # ----------------------------------------------------

        conversation_service = ConversationService(
            llm_service=self._get_llm_service()
        )

        # ----------------------------------------------------
        # 3. Load session
        # ----------------------------------------------------

        try:

            session = (
                conversation_service.get_session(
                    session_id=session_id
                )
            )

        except ValueError as exc:

            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ----------------------------------------------------
        # 4. Process question
        # ----------------------------------------------------

        try:

            response_text = (
                conversation_service.process_question(
                    session=session,
                    user_question=message,
                )
            )

        except ValueError as exc:

            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except RuntimeError as exc:

            return Response(
                {"detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # ----------------------------------------------------
        # 5. Retrieve assistant message
        # ----------------------------------------------------

        assistant_message = (
            session.messages
            .filter(
                role="assistant"
            )
            .order_by(
                "-created_at"
            )
            .first()
        )

        if assistant_message is None:

            return Response(
                {
                    "detail":
                        "Assistant response was generated "
                        "but could not be retrieved."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ----------------------------------------------------
        # 6. Serialize output
        # ----------------------------------------------------

        response_data = {

            "session_id":
                session.id,

            "message_id":
                assistant_message.id,

            "role":
                assistant_message.role,

            "content":
                response_text,

            "created_at":
                assistant_message.created_at,
        }

        response_serializer = ChatResponseSchema(
            response_data
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    # ========================================================
    # LLM Dependency
    # ========================================================

    @staticmethod
    def _get_llm_service():

        from core_next.services.llm.llm_service import (
            LLMService,
        )

        from core_next.services.llm.providers.ollama_provider import (
            OllamaProvider,
        )

        provider = OllamaProvider(
            model="qwen2.5:7b"
        )

        return LLMService(
            provider=provider
        )


# ============================================================
# Conversation Detail View
# ============================================================

class ConversationDetailView(APIView):
    """
    Retrieve a conversation and its message history.
    """

    def get(
        self,
        request,
        session_id,
    ):

        conversation_service = (
            ConversationService()
        )

        try:

            session = (
                conversation_service.get_session(
                    session_id=session_id
                )
            )

        except ValueError as exc:

            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ConversationSessionSchema(
            session
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )