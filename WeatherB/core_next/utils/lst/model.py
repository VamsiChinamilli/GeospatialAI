"""
model.py

ResNet34 U-Net for Land Surface Temperature (LST) regression.

Input
-----
(5, 256, 256)

Output
------
(1, 256, 256)

The model predicts temperature in Kelvin.
"""

import torch.nn as nn

# -------------------------------------------------------
# Reuse the proven U-Net components
# -------------------------------------------------------

from core_next.utils.unet.encoder import ResNet34Encoder
from core_next.utils.unet.decoder import Decoder


class LSTUNet(nn.Module):

    def __init__(
    self,
    in_channels=4,
    pretrained=True
):

        super().__init__()

        # -------------------------------------------------
        # Encoder
        # -------------------------------------------------

        self.encoder = ResNet34Encoder(
            in_channels=in_channels,
            pretrained=pretrained
        )

        # -------------------------------------------------
        # Decoder
        # -------------------------------------------------

        self.decoder = Decoder()

        # -------------------------------------------------
        # Regression Head
        # -------------------------------------------------

        self.head = nn.Sequential(

            nn.Conv2d(
                64,
                32,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(inplace=True),

            nn.Conv2d(
                32,
                1,
                kernel_size=1
            )

        )

    # -----------------------------------------------------

    def forward(self, x):

        x0, x1, x2, x3, x4 = self.encoder(x)

        x = self.decoder(
            x0,
            x1,
            x2,
            x3,
            x4
        )

        x = self.head(x)

        return x