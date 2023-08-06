import sys
from .nets import SwinIR
import torch
from torch import nn
import torch.nn.functional as F
from torchvision import transforms
import os
from ..utils import check_ckpt_exist, convert_image_type, get_url_id


class Upsampler(nn.Module):
    def __init__(self, folder_name='upsampler',  ckpt_name = 'upsampler_SwinIR_large.pth', force=False, device='cuda'):
        super(Upsampler, self).__init__()
        self.device = device
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        ckpt =  torch.load(ckpt_path)
        self.sr_net = SwinIR(upscale=4, in_chans=3, img_size=64, window_size=8,
                         img_range=1., depths=[6, 6, 6, 6, 6, 6, 6, 6, 6], embed_dim=240,
                         num_heads=[8, 8, 8, 8, 8, 8, 8, 8, 8],
                         mlp_ratio=2, upsampler='nearest+conv', resi_connection='3conv')
        self.sr_net.load_state_dict(ckpt['params_ema'], strict=True)
        self.sr_net.to(self.device)
        for param in self.sr_net.parameters():
            param.requires_grad = False
        self.sr_net.eval()
        del ckpt
        
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((256,256))
        ])
        
        
    def forward(self, x):
        W, H = x.size()[-1] ,x.size()[-2] 
        if W!=256 or H!=256:
            x = F.interpolate(x, (256,256), mode='bilinear')
        
        with torch.no_grad():
            return self.sr_net(x)
    
    def data_preprocess(self, input, unsqueeze = True):
        '''
        if unsqueeze == True, return (1,3,H,W)
        else return (3,W,H)
        default is True
        '''
        pil_img = convert_image_type(input)
        tensor_img = self.transform(pil_img).to(self.device)
        
        if unsqueeze:
            return tensor_img.unsqueeze(0)

        return tensor_img
        
    def data_postprocess(self, tensor_img):
        img_arr = tensor_img.squeeze().cpu().numpy().clip(0,1).transpose([1,2,0])*255
        return img_arr[:,:,::-1]
        
        
