"""
analysis.py

DRF serializers for geospatial analysis records.

Responsibilities
----------------
- Serialize AnalysisRecord instances.
- Validate analysis creation data.
- Provide complete and lightweight analysis representations.

This module does NOT:
- Run ML models.
- Perform raster processing.
- Calculate LST.
- Generate LLM responses.
- Manage conversation state.
"""

from rest_framework import serializers

from core_next.models import AnalysisRecord


# ============================================================
# Analysis Record
# ============================================================

class AnalysisRecordSchema(
    serializers.ModelSerializer
):
    """
    Full representation of an AnalysisRecord.
    """

    class Meta:

        model = AnalysisRecord

        fields = (
            "id",
            "bbox",
            "analysis_metrics",
            "model_metadata",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


# ============================================================
# Analysis Create
# ============================================================

class AnalysisCreateSchema(
    serializers.Serializer
):
    """
    Validate a new analysis request.
    """

    bbox = serializers.ListField(
        child=serializers.FloatField(),
        min_length=4,
        max_length=4,
        required=True,
    )

    def validate_bbox(self, value):

        min_lon, min_lat, max_lon, max_lat = value

        if min_lon >= max_lon:
            raise serializers.ValidationError(
                "min_lon must be less than max_lon."
            )

        if min_lat >= max_lat:
            raise serializers.ValidationError(
                "min_lat must be less than max_lat."
            )

        if not -180 <= min_lon <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )

        if not -180 <= max_lon <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )

        if not -90 <= min_lat <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )

        if not -90 <= max_lat <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )

        return value


# ============================================================
# Analysis Summary
# ============================================================

class AnalysisSummarySchema(
    serializers.ModelSerializer
):
    """
    Lightweight representation of an analysis.
    """

    class Meta:

        model = AnalysisRecord

        fields = (
            "id",
            "bbox",
            "created_at",
        )

        read_only_fields = (
            "id",
            "created_at",
        )


# ============================================================
# Analysis Reference
# ============================================================

class AnalysisReferenceSchema(
    serializers.ModelSerializer
):
    """
    Minimal analysis reference containing only its ID.
    """

    class Meta:

        model = AnalysisRecord

        fields = (
            "id",
        )

        read_only_fields = (
            "id",
        )