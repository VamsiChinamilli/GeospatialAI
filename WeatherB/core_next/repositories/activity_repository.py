# core_next/repositories/activity_repository.py

from core_next.models import (
    AnalysisRecord,
    ActivityLog
)

from .base_repository import BaseRepository


class ActivityRepository(BaseRepository):
    """
    Repository for backend audit logging.
    """

    @staticmethod
    def log(
        analysis: AnalysisRecord,
        event: str,
        details=None
    ):

        return ActivityLog.objects.create(
            analysis=analysis,
            event=event,
            details=details or {}
        )

    @staticmethod
    def get_logs(analysis: AnalysisRecord):

        return (
            ActivityLog.objects
            .filter(analysis=analysis)
            .order_by("created_at")
        )

    @staticmethod
    def delete_logs(analysis: AnalysisRecord):

        deleted, _ = ActivityLog.objects.filter(
            analysis=analysis
        ).delete()

        return deleted