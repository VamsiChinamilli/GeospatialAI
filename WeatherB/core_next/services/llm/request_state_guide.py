"""
request_state_guide.py

Guide 1 — Request State Detection
----------------------------------

Determines whether a user's request is:

1. A first request for a new BBOX/location.
2. A follow-up request for the currently active BBOX.

This guide intentionally does NOT:
- call an LLM
- call Ollama
- inspect the user's natural-language question
- generate responses
- manage conversation history
- generate climate analysis

It only determines request/location state.
"""

from typing import Any, Dict, List, Optional



class RequestStateGuide:
    """
    Determines whether the current request belongs to the
    existing location/session or starts a new location context.
    """

    NEW_LOCATION = "NEW_LOCATION"
    FOLLOW_UP = "FOLLOW_UP"

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(self):
        pass

    # =====================================================
    # BBOX validation
    # =====================================================

    @staticmethod
    def _validate_bbox(
        bbox: Optional[List[float]],
    ) -> Optional[List[float]]:
        """
        Validate and normalize a BBOX.

        Expected format:

            [
                min_lon,
                min_lat,
                max_lon,
                max_lat
            ]

        Returns
        -------
        list or None
        """

        if bbox is None:
            return None

        if not isinstance(bbox, (list, tuple)):
            raise TypeError(
                "bbox must be a list or tuple."
            )

        if len(bbox) != 4:
            raise ValueError(
                "bbox must contain exactly 4 values: "
                "[min_lon, min_lat, max_lon, max_lat]."
            )

        try:
            bbox = [
                float(value)
                for value in bbox
            ]

        except (TypeError, ValueError) as exc:

            raise ValueError(
                "bbox must contain numeric values."
            ) from exc

        min_lon, min_lat, max_lon, max_lat = bbox

        if min_lon >= max_lon:

            raise ValueError(
                "bbox min_lon must be smaller than max_lon."
            )

        if min_lat >= max_lat:

            raise ValueError(
                "bbox min_lat must be smaller than max_lat."
            )

        if not (
            -180.0 <= min_lon <= 180.0
            and
            -180.0 <= max_lon <= 180.0
        ):

            raise ValueError(
                "Longitude values must be between "
                "-180 and 180."
            )

        if not (
            -90.0 <= min_lat <= 90.0
            and
            -90.0 <= max_lat <= 90.0
        ):

            raise ValueError(
                "Latitude values must be between "
                "-90 and 90."
            )

        return bbox

    # =====================================================
    # BBOX comparison
    # =====================================================

    @staticmethod
    def _same_bbox(
        current_bbox: List[float],
        previous_bbox: List[float],
        tolerance: float = 1e-9,
    ) -> bool:
        """
        Determine whether two BBOX values represent
        the same location.

        A tiny tolerance is used to avoid floating-point
        comparison problems.
        """

        if len(current_bbox) != 4:
            return False

        if len(previous_bbox) != 4:
            return False

        return all(
            abs(
                float(current)
                -
                float(previous)
            ) <= tolerance
            for current, previous
            in zip(
                current_bbox,
                previous_bbox
            )
        )

    # =====================================================
    # Main decision
    # =====================================================

    def determine(
        self,
        current_bbox: Optional[List[float]],
        previous_bbox: Optional[List[float]] = None,
        conversation_exists: bool = False,
    ) -> Dict[str, Any]:
        """
        Determine the state of the current request.

        Parameters
        ----------
        current_bbox:
            BBOX associated with the current request.

        previous_bbox:
            BBOX associated with the currently active
            conversation/session.

        conversation_exists:
            Whether an active conversation already exists.

        Returns
        -------
        dict

        Example — new location:

        {
            "request_type": "NEW_LOCATION",
            "is_new_location": True,
            "is_first_question": True,
            "same_bbox": False
        }

        Example — follow-up:

        {
            "request_type": "FOLLOW_UP",
            "is_new_location": False,
            "is_first_question": False,
            "same_bbox": True
        }
        """

        current_bbox = self._validate_bbox(
            current_bbox
        )

        previous_bbox = self._validate_bbox(
            previous_bbox
        )

        # -------------------------------------------------
        # No current location
        # -------------------------------------------------

        if current_bbox is None:

            raise ValueError(
                "current_bbox is required."
            )

        # -------------------------------------------------
        # No previous conversation/location
        # -------------------------------------------------

        if (
            not conversation_exists
            or
            previous_bbox is None
        ):

            return {

                "request_type":
                    self.NEW_LOCATION,

                "is_new_location":
                    True,

                "is_first_question":
                    True,

                "same_bbox":
                    False,

            }

        # -------------------------------------------------
        # Compare locations
        # -------------------------------------------------

        same_bbox = self._same_bbox(
            current_bbox,
            previous_bbox
        )

        # -------------------------------------------------
        # Same location → follow-up
        # -------------------------------------------------

        if same_bbox:

            return {

                "request_type":
                    self.FOLLOW_UP,

                "is_new_location":
                    False,

                "is_first_question":
                    False,

                "same_bbox":
                    True,

            }

        # -------------------------------------------------
        # Different location → new context
        # -------------------------------------------------

        return {

            "request_type":
                self.NEW_LOCATION,

            "is_new_location":
                True,

            "is_first_question":
                True,

            "same_bbox":
                False,

        }


# =========================================================
# Simple standalone test
# =========================================================

if __name__ == "__main__":

    guide = RequestStateGuide()

    print("\n" + "=" * 60)
    print("REQUEST STATE GUIDE TEST")
    print("=" * 60)

    # -----------------------------------------------------
    # Test 1 — first request
    # -----------------------------------------------------

    result = guide.determine(

        current_bbox=[
            80.60,
            16.48,
            80.62,
            16.50
        ],

        previous_bbox=None,

        conversation_exists=False

    )

    print("\nTEST 1 — First request")
    print(result)

    # -----------------------------------------------------
    # Test 2 — same BBOX
    # -----------------------------------------------------

    result = guide.determine(

        current_bbox=[
            80.60,
            16.48,
            80.62,
            16.50
        ],

        previous_bbox=[
            80.60,
            16.48,
            80.62,
            16.50
        ],

        conversation_exists=True

    )

    print("\nTEST 2 — Same BBOX")
    print(result)

    # -----------------------------------------------------
    # Test 3 — different BBOX
    # -----------------------------------------------------

    result = guide.determine(

        current_bbox=[
            80.70,
            16.55,
            80.72,
            16.57
        ],

        previous_bbox=[
            80.60,
            16.48,
            80.62,
            16.50
        ],

        conversation_exists=True

    )

    print("\nTEST 3 — Different BBOX")
    print(result)

    print("\n" + "=" * 60)
    print("REQUEST STATE GUIDE TEST COMPLETED")
    print("=" * 60)