import os
import sys
sys.path.append('../')
import cv2
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F

import torchvision.transforms as transforms

from .nets import MyGenerator
from ..utils import check_ckpt_exist, convert_image_type, get_url_id


class HWCT(nn.Module):
    
    def __init__(self, img_size : int = 512, folder_name='head_color_transfer', ckpt_name = 'G_128_512_head_60k.pt', force=False, device='cuda'):
        '''
        Related Links
        --------
        https://github.com/jmliu88/HeSer

        Methods
        --------
        - forward
            - Input
                - source_rgb
                    - dtype : tensor
                    - shape : (b, 3, 512, 512)
                    - min max : (-1, 1)
                - target_rgb  
                    - if you only have gray scale image, you should repeat gray scale image's channel to fit amount of rgb channel amount
                    - dtype : tensor
                    - shape : (b, 3, 512, 512)
                    - min max : (-1, 1)
                - source_onehot
                    - dtype : tensor
                    - shape : (b, 19, 512, 512)
                    - min max : (0 or 1)
                - target_onehot
                    - dtype : tensor
                    - shape : (b, 19, 512, 512)
                    - min max : (0 or 1)
                - target_gray
                    - dtype : tensor
                    - shape : (b, 1, 512, 512)
                    - min max : (-1, 1)
                - target_face_mask
                    - dtype : tensor
                    - shape : (b, 1, 512, 512)
                    - min max : (0 or 1)
                
            - Output
                - result
                    - shape : (1, 3, 512, 512)
                    - min max : (-1, 1)
                - color reference map
                    - shape : (1, 3, 512, 512))
                    - min max : (-1, 1)
        
        '''
        super(HWCT, self).__init__()
        self.img_size = img_size
        self.device = device
        self.generator = MyGenerator().to(self.device)
        
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        ckpt = torch.load(ckpt_path, map_location=self.device)
       
        self.generator.load_state_dict(ckpt['model'], strict=True)
        for param in self.generator.parameters():
            param.requires_grad = False
        self.generator.eval()
        del ckpt

    def forward(self, source_rgb, target_rgb, source_onehot, target_onehot, target_gray, target_face_mask):
        """
        Input
        ---------
            - source_rgb
                - dtype : tensor
                - shape : (b, 3, 512, 512)
                - min max : (-1, 1)
            - target_rgb  
                - if you only have gray scale image, you should repeat gray scale image's channel to fit amount of rgb channel amount
                - dtype : tensor
                - shape : (b, 3, 512, 512)
                - min max : (-1, 1)
            - source_onehot
                - dtype : tensor
                - shape : (b, 19, 512, 512)
                - min max : (0 or 1)
            - target_onehot
                - dtype : tensor
                - shape : (b, 19, 512, 512)
                - min max : (0 or 1)
            - target_gray
                - dtype : tensor
                - shape : (b, 1, 512, 512)
                - min max : (-1, 1)
            - target_face_mask
                - dtype : tensor
                - shape : (b, 1, 512, 512)
                - min max : (0 or 1)
            
        Output
        ---------
            - result
                - shape : (1, 3, 512, 512)
                - min max : (-1, 1)
            - color reference map
                - shape : (1, 3, 512, 512))
                - min max : (-1, 1)
        """
        result, color_reference_map = self.generator(source_rgb, target_rgb, source_onehot, target_onehot, target_gray, target_face_mask)
        return result, color_reference_map
        