import torch.nn as nn

from .encoder import ResNet34Encoder
from .decoder import Decoder


class UNet(nn.Module):

    def __init__(
        self,
        in_channels=5,
        num_classes=11,
        pretrained=True
    ):
        super().__init__()

        # ---------------------------------------------
        # Encoder
        # ---------------------------------------------

        self.encoder = ResNet34Encoder(
            in_channels=in_channels,
            pretrained=pretrained
        )

        # ---------------------------------------------
        # Decoder
        # ---------------------------------------------

        self.decoder = Decoder()

        # ---------------------------------------------
        # Segmentation Head
        # ---------------------------------------------

        self.head = nn.Conv2d(
            in_channels=64,
            out_channels=num_classes,
            kernel_size=1
        )

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