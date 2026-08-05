import cv2
import numpy as np
import torch

from core_next.utils.model_loader import ModelLoader


CLASS_NAMES = {
    0: "builtup",
    1: "water",
    2: "vegetation",
}


class InferenceService:

    def __init__(self):

        self.model = ModelLoader.load_unet()

    def run(self, raster):

        """
        Parameters
        ----------
        raster : numpy.ndarray
            Shape = (4, H, W)
            Order = Blue, Green, Red, NIR

        Returns
        -------
        {
            "mask": ...,
            "land_cover": ...
        }
        """

        input_tensor = self._preprocess(raster)

        with torch.no_grad():

            logits = self.model(input_tensor)

            prediction = torch.argmax(
                logits,
                dim=1
            )

        mask = prediction.squeeze().cpu().numpy().astype(np.uint8)

        land_cover = self._calculate_percentages(mask)

        return {
            "mask": mask,
            "land_cover": land_cover,
        }

    def _preprocess(self, raster):

        """
        Converts

        (4,H,W)

        →

        (1,4,256,256)
        """

        bands = []

        for band in raster:

            resized = cv2.resize(
                band,
                (256, 256),
                interpolation=cv2.INTER_LINEAR,
            )

            bands.append(resized.astype(np.float32))

        image = np.stack(bands)

        tensor = torch.from_numpy(image)

        tensor = tensor.unsqueeze(0)

        return tensor

    def _calculate_percentages(self, mask):

        total = mask.size

        result = {}

        for class_id, class_name in CLASS_NAMES.items():

            pixels = np.sum(mask == class_id)

            result[class_name] = round(
                (pixels / total) * 100,
                2,
            )

        return result