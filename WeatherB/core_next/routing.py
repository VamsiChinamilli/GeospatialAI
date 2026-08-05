"""
routing.py

WebSocket URL routing for the Urban Climate Copilot.
"""

from django.urls import path

from core_next.consumers import (
UrbanCopilotConsumer,
)

urlpatterns = [


path(
    "ws/chat/<uuid:session_id>/",
    UrbanCopilotConsumer.as_asgi(),
),


]
