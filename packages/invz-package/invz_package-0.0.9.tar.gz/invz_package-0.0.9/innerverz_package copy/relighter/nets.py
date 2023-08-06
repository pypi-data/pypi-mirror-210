import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from .utils.blocks import ConvBlock, AdaINResBlock

class MLP(nn.Module):
    # TODO: input_nc check!
    def __init__(self, input_nc=3, output_nc=512):
        super(MLP, self).__init__()
        
        self.linear_0 = nn.Linear(input_nc, output_nc)
        self.linear_1 = nn.Linear(output_nc, output_nc)
        self.linear_2 = nn.Linear(output_nc, output_nc)
        self.linear_3 = nn.Linear(output_nc, output_nc)
        
    def forward(self, input):
        output = self.linear_0(input)
        output = self.linear_1(output)
        output = self.linear_2(output)
        output = self.linear_3(output)
        
        return output

class Unet(nn.Module):
    def __init__(self, input_nc=3, output_nc=3):
        super(Unet, self).__init__()
        
        self.input_layer = nn.Sequential(nn.ReflectionPad2d(3), nn.Conv2d(input_nc, 32, kernel_size=7))

        self.down1 = AdaINResBlock(32, 64, scale_factor=.5)
        self.down2 = AdaINResBlock(64, 128, scale_factor=.5)
        self.down3 = AdaINResBlock(128, 256, scale_factor=.5)
        self.down4 = AdaINResBlock(256, 512, scale_factor=.5)
        
        self.bottle_neck = AdaINResBlock(512, 512, scale_factor=1)
                           
        self.up4 = AdaINResBlock(1024, 256, scale_factor=2)
        self.up3 = AdaINResBlock(512, 128, scale_factor=2)
        self.up2 = AdaINResBlock(256, 64, scale_factor=2)
        self.up1 = AdaINResBlock(128, 32, scale_factor=2)

        self.output_layer = nn.Sequential(nn.ReflectionPad2d(3), nn.Conv2d(32, output_nc, kernel_size=7))

    def forward(self, x, style):

        x_in = self.input_layer(x)

        x_d1 = self.down1(x_in, style)
        x_d2 = self.down2(x_d1, style)
        x_d3 = self.down3(x_d2, style)
        x_d4 = self.down4(x_d3, style)

        x_bn = self.bottle_neck(x_d4, style)

        x_u4 = self.up4(torch.cat([x_d4,x_bn], dim=1), style)
        x_u3 = self.up3(torch.cat([x_d3,x_u4], dim=1), style)
        x_u2 = self.up2(torch.cat([x_d2,x_u3], dim=1), style)
        x_u1 = self.up1(torch.cat([x_d1,x_u2], dim=1), style)

        x_out = self.output_layer(x_u1)

        return x_out
        # return F.tanh(x_out) * 2

class MyGenerator(nn.Module):
    def __init__(self):
        super(MyGenerator, self).__init__()
        self.mlp = MLP(36+128+512,512)
        self.unet = Unet(2, 1)

    def forward(self, target_face, source_shape, source_params):
        input_images = torch.cat([target_face, source_shape], dim=1)
        
        input_params = self.mlp(source_params)
        outputs = self.unet(input_images, input_params)

        return outputs
    
