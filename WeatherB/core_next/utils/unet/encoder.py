import torch
import torch.nn as nn
from torchvision.models import resnet34, ResNet34_Weights


class ResNet34Encoder(nn.Module):

    def __init__(self, in_channels=5, pretrained=True):
        super().__init__()

        if pretrained:
            backbone = resnet34(
                weights=ResNet34_Weights.IMAGENET1K_V1
            )
        else:
            backbone = resnet34(weights=None)

        # -------------------------------------------------
        # Replace first convolution (3 → 5 channels)
        # -------------------------------------------------

        old_conv = backbone.conv1

        backbone.conv1 = nn.Conv2d(
            in_channels,
            old_conv.out_channels,
            kernel_size=old_conv.kernel_size,
            stride=old_conv.stride,
            padding=old_conv.padding,
            bias=False
        )

        with torch.no_grad():

            backbone.conv1.weight[:, :3] = old_conv.weight

            backbone.conv1.weight[:, 3:] = (
                old_conv.weight[:, :2].mean(
                    dim=1,
                    keepdim=True
                )
            )

        # -------------------------------------------------
        # Encoder stages
        # -------------------------------------------------

        self.layer0 = nn.Sequential(
            backbone.conv1,
            backbone.bn1,
            backbone.relu
        )

        self.pool = backbone.maxpool

        self.layer1 = backbone.layer1
        self.layer2 = backbone.layer2
        self.layer3 = backbone.layer3
        self.layer4 = backbone.layer4

    def forward(self, x):

        x0 = self.layer0(x)

        x1 = self.layer1(self.pool(x0))

        x2 = self.layer2(x1)

        x3 = self.layer3(x2)

        x4 = self.layer4(x3)

        return x0, x1, x2, x3, x4