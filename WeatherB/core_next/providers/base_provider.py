# core_next/providers/base_provider.py

from abc import ABC, abstractmethod


class BaseRasterProvider(ABC):

    @abstractmethod
    def get_best_scene(self, bbox):
        """
        Return the best STAC item for the given bbox.
        """
        pass

    @abstractmethod
    def get_band_mapping(self):
        """
        Return provider-specific band names.
        Example:
        {
            "red": "B04",
            "green": "B03",
            "blue": "B02",
            "nir": "B08"
        }
        """
        pass

    @abstractmethod
    def get_metadata(self):
        """
        Return provider information.
        """
        pass