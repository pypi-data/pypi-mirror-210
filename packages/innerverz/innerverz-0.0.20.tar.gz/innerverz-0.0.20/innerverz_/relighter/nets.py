import torch
import torch.nn as nn
import torch.nn.functional as F

class AdaIN(nn.Module):
    def __init__(self, style_dim, num_features):
        super().__init__()
        self.norm = nn.InstanceNorm2d(num_features, affine=False)
        self.fc = nn.Linear(style_dim, num_features*2)

    def forward(self, x, s):
        h = self.fc(s)
        h = h.view(h.size(0), h.size(1), 1, 1)
        gamma, beta = torch.chunk(h, chunks=2, dim=1)
        return (1 + gamma) * self.norm(x) + beta

class AdaINResBlock(nn.Module):
    def __init__(self, in_c, out_c, scale_factor=1, style_dim=512):
        super(AdaINResBlock, self).__init__()

        self.conv1 = nn.Conv2d(in_channels=in_c, out_channels=out_c, kernel_size=3, stride=1, padding=1, padding_mode='reflect', bias=False)
        self.AdaIN1 = AdaIN(style_dim, out_c)
        self.activ1 = nn.LeakyReLU(0.2)

        self.conv2 = nn.Conv2d(in_channels=out_c, out_channels=out_c, kernel_size=3, stride=1, padding=1, padding_mode='reflect', bias=False)
        self.AdaIN2 = AdaIN(style_dim, out_c)
        self.activ2 = nn.LeakyReLU(0.2)

        self.conv1x1 = nn.Conv2d(in_channels=in_c, out_channels=out_c, kernel_size=1, stride=1, padding=0, padding_mode='reflect', bias=False)

        self.scale_factor = scale_factor
        self.resize = scale_factor != 1

    def forward(self, feat, style):

        feat1 = feat
        feat1 = self.conv1(feat1)
        feat1 = self.AdaIN1(feat1, style)
        feat1 = self.activ1(feat1)

        if self.resize:
            feat1 = F.interpolate(feat1, scale_factor=self.scale_factor, mode='bilinear')

        feat1 = self.conv2(feat1)
        feat1 = self.AdaIN2(feat1, style)
        feat1 = self.activ2(feat1)

        # skip connction
        feat2 = feat
        if self.resize:
            feat2 = F.interpolate(feat2, scale_factor=self.scale_factor, mode='bilinear') # size
            feat2 = self.conv1x1(feat2) # chnnel dim

        return feat1 + feat2


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
    
