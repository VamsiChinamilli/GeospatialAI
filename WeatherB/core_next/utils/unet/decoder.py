import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------------------------------------
# Double Convolution
# ---------------------------------------------------------

class DoubleConv(nn.Module):

    def __init__(self, in_channels, out_channels):

        super().__init__()

        self.block = nn.Sequential(

            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False
            ),

            nn.BatchNorm2d(out_channels),

            nn.ReLU(inplace=True),

            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False
            ),

            nn.BatchNorm2d(out_channels),

            nn.ReLU(inplace=True)

        )

    def forward(self, x):

        return self.block(x)


# ---------------------------------------------------------
# Decoder Block
# ---------------------------------------------------------

class DecoderBlock(nn.Module):

    def __init__(
        self,
        in_channels,
        skip_channels,
        out_channels
    ):

        super().__init__()

        self.conv = DoubleConv(
            in_channels + skip_channels,
            out_channels
        )

    def forward(
        self,
        x,
        skip
    ):

        x = F.interpolate(

            x,

            size=skip.shape[-2:],

            mode="bilinear",

            align_corners=False

        )

        x = torch.cat(

            [

                x,

                skip

            ],

            dim=1

        )

        return self.conv(x)


# ---------------------------------------------------------
# Decoder
# ---------------------------------------------------------

class Decoder(nn.Module):

    def __init__(self):

        super().__init__()

        self.dec4 = DecoderBlock(
            512,
            256,
            256
        )

        self.dec3 = DecoderBlock(
            256,
            128,
            128
        )

        self.dec2 = DecoderBlock(
            128,
            64,
            64
        )

        self.dec1 = DecoderBlock(
            64,
            64,
            64
        )

        self.final = DoubleConv(
            64,
            64
        )

    def forward(

        self,

        x0,

        x1,

        x2,

        x3,

        x4

    ):

        x = self.dec4(x4, x3)

        x = self.dec3(x, x2)

        x = self.dec2(x, x1)

        x = self.dec1(x, x0)

        x = F.interpolate(

            x,

            scale_factor=2,

            mode="bilinear",

            align_corners=False

        )

        x = self.final(x)

        return x