import numpy as np


class FeatureExtractor:
    """
    Converts a segmentation mask and temperature grid
    into numerical features for the regression model.
    """

    @staticmethod
    def extract(mask: np.ndarray, temperature_grid: np.ndarray) -> dict:

        # Ignore invalid temperatures
        valid = ~np.isnan(temperature_grid)

        if np.count_nonzero(valid) == 0:
            raise ValueError("No valid temperature pixels found.")

        valid_mask = mask[valid]
        valid_temp = temperature_grid[valid]

        total_pixels = len(valid_mask)

        buildup_pct = float(
            np.sum(valid_mask == 0) / total_pixels * 100
        )

        water_pct = float(
            np.sum(valid_mask == 1) / total_pixels * 100
        )

        vegetation_pct = float(
            np.sum(valid_mask == 2) / total_pixels * 100
        )

        min_temp = float(np.min(valid_temp))
        max_temp = float(np.max(valid_temp))
        mean_temp = float(np.mean(valid_temp))
        temp_variance = float(np.var(valid_temp))

        # hottest pixel
        hottest_index = np.nanargmax(temperature_grid)

        # coldest pixel
        coldest_index = np.nanargmin(temperature_grid)

        flat_mask = mask.reshape(-1)

        hotspot_class = int(flat_mask[hottest_index])
        coldspot_class = int(flat_mask[coldest_index])

        return {

            "buildup_percent": buildup_pct,

            "water_percent": water_pct,

            "veg_percent": vegetation_pct,

            "min_temp": min_temp,

            "max_temp": max_temp,

            "mean_temp": mean_temp,

            "temp_variance": temp_variance,

            "hotspot_dominant_class": hotspot_class,

            "coldspot_dominant_class": coldspot_class,

        }