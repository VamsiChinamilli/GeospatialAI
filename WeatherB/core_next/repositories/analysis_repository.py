# core_next/repositories/analysis_repository.py

from typing import Optional

from core_next.models import AnalysisRecord


class AnalysisRepository:
    """
    Repository responsible ONLY for AnalysisRecord CRUD operations.
    """

    @staticmethod
    def create_analysis(
        bbox,
        analysis_metrics,
        model_metadata=None,
    ) -> AnalysisRecord:

        return AnalysisRecord.objects.create(
            bbox=bbox,
            analysis_metrics=analysis_metrics,
            model_metadata=model_metadata or {},
        )

    @staticmethod
    def get_by_id(analysis_id) -> Optional[AnalysisRecord]:

        return (
            AnalysisRecord.objects
            .filter(id=analysis_id)
            .first()
        )

    @staticmethod
    def get_by_bbox(bbox) -> Optional[AnalysisRecord]:

        return (
            AnalysisRecord.objects
            .filter(bbox=bbox)
            .first()
        )

    @staticmethod
    def get_recent(limit=20):

        return (
            AnalysisRecord.objects
            .order_by("-created_at")[:limit]
        )

    @staticmethod
    def update_metrics(
        analysis,
        metrics,
    ):

        analysis.analysis_metrics = metrics
        analysis.save(update_fields=["analysis_metrics", "updated_at"])

        return analysis

    @staticmethod
    def delete(analysis):

        analysis.delete()