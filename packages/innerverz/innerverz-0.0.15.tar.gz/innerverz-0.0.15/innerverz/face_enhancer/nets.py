import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    def __init__(self, input_dim ,output_dim, kernel_size=3, stride=2, padding=1, \
        norm_type='bn', act_type='lrelu', transpose=False):
        super(ConvBlock, self).__init__()

        # convolutional layer and upsampling
        self.up = transpose
        self.scale_factor = stride

        if transpose:
            self.conv = nn.Conv2d(input_dim, output_dim, kernel_size, stride=1, padding=padding, padding_mode='reflect', bias=False)
        else:
            self.conv = nn.Conv2d(input_dim, output_dim, kernel_size, stride, padding=padding, padding_mode='reflect', bias=False)
        
        # normalization
        if norm_type == 'bn':
            self.norm = nn.BatchNorm2d(output_dim)
        elif norm_type == 'in':
            self.norm = nn.InstanceNorm2d(output_dim)
        elif norm_type == 'none':
            self.norm = None
        else:
            assert 0, f"Unsupported normalization: {norm_type}"
        
        # activation
        if act_type == 'relu':
            self.act = nn.ReLU()
        elif act_type == 'lrelu':
            self.act = nn.LeakyReLU(0.2)
        elif act_type == 'tanh':
            self.act = nn.Tanh()
        elif act_type == 'sig':
            self.act = nn.Sigmoid()
        elif act_type == 'none':
            self.act = None
        else:
            assert 0, f"Unsupported activation: {act_type}"


    def forward(self, x):
        if self.up:
            x = F.interpolate(x, scale_factor=self.scale_factor, mode='bilinear')

        x = self.conv(x)

        if self.norm:
            x = self.norm(x)

        if self.act:
            x = self.act(x)
        return x


class Unet(nn.Module):
    def __init__(self, input_nc=3, output_nc=3):
        super(Unet, self).__init__()
        
        self.input_layer = nn.Sequential(nn.ReflectionPad2d(1), nn.Conv2d(input_nc, 64, kernel_size=3))

        self.down1 = ConvBlock(64, 128)
        self.down2 = ConvBlock(128, 256)
        self.down3 = ConvBlock(256, 512)
        # self.down4 = ConvBlock(512, 512)
        # self.down5 = ConvBlock(512, 512)

        self.same1 = ConvBlock(512, 512, stride=1)
        self.same2 = ConvBlock(512, 512, stride=1)
        self.same3 = ConvBlock(512, 512, stride=1)
        self.same4 = ConvBlock(512, 512, stride=1)
        self.same5 = ConvBlock(512, 512, stride=1)
        self.same6 = ConvBlock(512, 512, stride=1)
                           
        # self.up5 = ConvBlock(512, 512, transpose=True)
        # self.up4 = ConvBlock(512, 512, transpose=True)
        self.up3 = ConvBlock(512, 256, transpose=True)
        self.up2 = ConvBlock(256, 128, transpose=True)
        self.up1 = ConvBlock(128, 64, transpose=True)

        self.to_rgb3 = nn.Sequential(nn.ReflectionPad2d(1), nn.Conv2d(256, output_nc, kernel_size=3))
        self.to_rgb2 = nn.Sequential(nn.ReflectionPad2d(1), nn.Conv2d(128, output_nc, kernel_size=3))
        self.to_rgb1 = nn.Sequential(nn.ReflectionPad2d(1), nn.Conv2d(64, output_nc, kernel_size=3))

    def forward(self, x):
        rgb = torch.zeros_like(x).clone().detach()

        x = self.input_layer(x)

        x = self.down1(x)
        x = self.down2(x)
        x = self.down3(x)
        
        skip = x
        x = self.same1(x)
        x = self.same2(x)
        x = self.same3(x)
        x = self.same4(x)
        x = self.same5(x)
        x = self.same6(x)
        x = x + skip

        x = self.up3(x)
        rgb += F.interpolate(self.to_rgb3(x), rgb.size()[-1], mode='bilinear')

        x = self.up2(x)
        rgb += F.interpolate(self.to_rgb2(x), rgb.size()[-1], mode='bilinear')

        x = self.up1(x)
        rgb += F.interpolate(self.to_rgb1(x), rgb.size()[-1], mode='bilinear')

        return rgb
        # return residual + skip, residual

class MyGenerator(nn.Module):
    def __init__(self):
        super(MyGenerator, self).__init__()
        self.unet = Unet(3, 3)

    def forward(self, LQ):

        output = self.unet(LQ)

        return output