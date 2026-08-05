"""
urls.py

URL configuration for core_next.

Routes
------
POST /api/analyze/
POST /api/chat/
GET  /api/chat/<session_id>/
"""

from django.urls import path

from core_next.views import (
    AnalysisView,
    ChatView,
    ConversationDetailView,
)


urlpatterns = [

    # --------------------------------------------------------
    # Analysis
    # --------------------------------------------------------

    path(
        "analyze/",
        AnalysisView.as_view(),
        name="analysis",
    ),

    # --------------------------------------------------------
    # Chat
    # --------------------------------------------------------

    path(
        "chat/",
        ChatView.as_view(),
        name="chat",
    ),

    # --------------------------------------------------------
    # Conversation
    # --------------------------------------------------------

    path(
        "chat/<uuid:session_id>/",
        ConversationDetailView.as_view(),
        name="conversation-detail",
    ),

]