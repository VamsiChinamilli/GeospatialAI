"""
models.py

Database models for the Urban Climate AI system.

Architecture
------------

One analysis creates exactly one conversation session.

    AnalysisRecord
          │
          │ one-to-one
          ▼
    ConversationSession
          │
          │ one-to-many
          ▼
      ChatMessage

The ConversationSession is the central lifecycle unit.

A session contains:
    - One analysis
    - One BBox through the analysis
    - Analysis results through the analysis
    - Conversation history through ChatMessage
    - Session metadata
    - Three-day expiration information

When a session is deleted:
    - Its analysis is deleted.
    - Its chat messages are deleted.
    - Its activity logs are deleted.

Automatic three-day cleanup is handled separately from
the Django model definitions.
"""

from datetime import timedelta
import uuid

from django.db import models
from django.utils import timezone


# ============================================================
# Session Expiry
# ============================================================

def default_expiry():
    """
    Return the default expiration time for a new session.

    Every session remains available for three days from
    the moment it is created.
    """

    return timezone.now() + timedelta(days=3)


# ============================================================
# Analysis Record
# ============================================================

class AnalysisRecord(models.Model):
    """
    Stores the geospatial analysis associated with one session.

    An AnalysisRecord is not an independent permanent record.

    Each analysis belongs to exactly one ConversationSession,
    and each ConversationSession belongs to exactly one analysis.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    bbox = models.JSONField(
        help_text=(
            "Bounding box in the format "
            "[min_lon, min_lat, max_lon, max_lat]."
        ),
    )

    analysis_metrics = models.JSONField(
        help_text=(
            "Complete climate analysis output including "
            "land-cover analysis and LST expert-system results."
        ),
    )

    model_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Metadata describing the models, expert system, "
            "raster provider, and other analysis components."
        ),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis {self.id}"


# ============================================================
# Conversation Session
# ============================================================

class ConversationSession(models.Model):
    """
    Central state container for one dashboard session.

    One session represents one complete interaction with
    one analyzed geographic region.

    A session owns:
        - exactly one AnalysisRecord
        - its conversation history
        - its lifecycle state
        - its expiration time

    The session is temporary and expires after three days.
    """

    REQUEST_TYPE_CHOICES = (
        ("NEW_LOCATION", "New Location"),
        ("FOLLOW_UP", "Follow Up"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    analysis = models.OneToOneField(
        AnalysisRecord,
        on_delete=models.CASCADE,
        related_name="conversation_session",
    )

    request_type = models.CharField(
        max_length=30,
        choices=REQUEST_TYPE_CHOICES,
        default="NEW_LOCATION",
    )

    is_first_question = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    last_active = models.DateTimeField(
        auto_now=True,
    )

    expires_at = models.DateTimeField(
        default=default_expiry,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Session {self.id}"

    @property
    def is_expired(self):
        """
        Return True when the session has passed its expiry time.
        """

        return timezone.now() >= self.expires_at


# ============================================================
# Chat Message
# ============================================================

class ChatMessage(models.Model):
    """
    Stores one message belonging to a conversation session.

    Messages are intentionally attached directly to the session
    because the session is the central conversation container.

    The conversation service is responsible for retaining only
    the latest three user/assistant exchanges.
    """

    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    conversation = models.ForeignKey(
        ConversationSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role} message ({self.id})"


# ============================================================
# Activity Log
# ============================================================

class ActivityLog(models.Model):
    """
    Stores temporary activity information associated with
    an analysis/session lifecycle.

    Activity logs are deleted automatically when their
    AnalysisRecord is deleted.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    analysis = models.ForeignKey(
        AnalysisRecord,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )

    event = models.CharField(
        max_length=100,
    )

    details = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.event