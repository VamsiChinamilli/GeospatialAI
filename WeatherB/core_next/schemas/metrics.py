"""
metrics.py

Serializers for structured geospatial climate metrics.

Responsibilities
----------------
- Validate structured land-cover metrics.
- Validate LST metrics.
- Validate environmental effects.
- Validate contributor information.
- Provide a consistent API representation of analysis metrics.

This module does NOT:
- Run ML models.
- Process satellite imagery.
- Calculate LST.
- Perform raster analysis.
- Generate LLM responses.
"""


from rest_framework import serializers


# ============================================================
# Land-Cover Metrics
# ============================================================

class LandCoverMetricsSchema(
    serializers.Serializer
):
    """
    Structured land-cover analysis.

    Example
    -------
    {
        "class_percentages": {
            "Built-up": 42.0,
            "Tree Cover": 28.0
        },
        "dominant_class": "Built-up"
    }
    """

    class_percentages = serializers.DictField(
        child=serializers.FloatField(
            min_value=0
        )
    )

    dominant_class = serializers.CharField(
        allow_blank=True,
        required=False
    )


# ============================================================
# Land-Cover Temperature Effects
# ============================================================

class LandCoverEffectsSchema(
    serializers.DictField
):
    """
    Temperature effects associated with land-cover classes.

    Example
    -------
    {
        "Built-up": 4.20,
        "Tree Cover": -1.68
    }
    """

    child = serializers.FloatField()


# ============================================================
# Environmental Effects
# ============================================================

class EnvironmentalEffectsSchema(
    serializers.DictField
):
    """
    Environmental factors contributing to the
    supplied temperature estimate.

    Example
    -------
    {
        "season": 1.50,
        "solar": 0.80,
        "vegetation": -0.30
    }
    """

    child = serializers.FloatField()


# ============================================================
# Expected LST Range
# ============================================================

class ExpectedLSTRangeSchema(
    serializers.Serializer
):
    """
    Expected range associated with the supplied
    LST estimate.
    """

    min = serializers.FloatField()

    max = serializers.FloatField()

    def validate(self, attrs):
        """
        Ensure the minimum does not exceed the maximum.
        """

        minimum = attrs.get("min")
        maximum = attrs.get("max")

        if (
            minimum is not None
            and maximum is not None
            and minimum > maximum
        ):
            raise serializers.ValidationError(
                "Expected LST minimum cannot be "
                "greater than maximum."
            )

        return attrs


# ============================================================
# LST Metrics
# ============================================================

class LSTMetricsSchema(
    serializers.Serializer
):
    """
    Structured Land Surface Temperature analysis.

    The value is treated as an application-generated
    estimate, not a direct ground measurement.
    """

    estimated_lst_celsius = serializers.FloatField()

    expected_range_celsius = (
        ExpectedLSTRangeSchema()
    )

    classification = serializers.CharField(
        allow_blank=True,
        required=False
    )

    confidence = serializers.FloatField(
        min_value=0,
        max_value=1,
        required=False,
        allow_null=True
    )

    land_cover_effects = (
        LandCoverEffectsSchema(
            required=False
        )
    )

    environmental_effects = (
        EnvironmentalEffectsSchema(
            required=False
        )
    )

    main_contributors = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


# ============================================================
# Complete Analysis Metrics
# ============================================================

class AnalysisMetricsSchema(
    serializers.Serializer
):
    """
    Complete structured metrics produced by the
    geospatial analysis pipeline.
    """

    land_cover = LandCoverMetricsSchema()

    lst = LSTMetricsSchema()


# ============================================================
# Metrics Validation Helper
# ============================================================

def validate_analysis_metrics(
    metrics
):
    """
    Validate a complete analysis metrics dictionary.

    This helper is useful when metrics are generated
    internally by the analysis pipeline before being
    stored inside AnalysisRecord.analysis_metrics.
    """

    serializer = AnalysisMetricsSchema(
        data=metrics
    )

    serializer.is_valid(
        raise_exception=True
    )

    return serializer.validated_data