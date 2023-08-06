import os
cwd = os.path.dirname(os.path.realpath(__file__))

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from ..utils import check_ckpt_exist, convert_image_type, get_url_id
from .nets import MyGenerator

class DeBlurrer(nn.Module):
    def __init__(self, size=1024, folder_name='deblurrer', ckpt_name='G_1024_65000.pt', force=False, device='cuda'):
        super(DeBlurrer, self).__init__()
        self.device = device
        self.size = size
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        ckpt = torch.load(ckpt_path, map_location=self.device)
        
        self.deblurrer = MyGenerator().to(self.device)
        self.deblurrer.load_state_dict(ckpt['model'])
        for param in self.deblurrer.parameters():
            param.requires_grad = False
        self.deblurrer.eval()
        del ckpt

        self.GaussianBlur = transforms.GaussianBlur(kernel_size=5, sigma=(0.1, 5))
        self.kernel = torch.ones((1,1,5,5), device=self.device)

        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((self.size,self.size)),
            transforms.Normalize([.5,.5,.5], [.5,.5,.5])
        ])

    def forward(self, tensor_image):
        """
        Input
        ---------
            - dtype : tensor
            - shape : (1, 3, 1024, 1024)
            - min max : (-1, 1)
            
            
        Output
        ---------
            - dtype : tensor
            - shape : (1, 3, 1024, 1024)
            - min max : (-1, 1)
        """
        
        fake, fake_res, edge = self.deblurrer(tensor_image)
        return fake, fake_res, edge

    def data_preprocess(self, input, unsqueeze=True):
        """
        Input
        ---------
            - dtype : image_path(str) or cv2 image or pillow image
            - shape : (h, w, 3)
            - min max : (0, 255)
            
        Output
        ---------
            - shape : (1, 3, 1024, 1024)
            - min max : (-1, 1)
        """
        pil_img = convert_image_type(input)
        tensor_img = self.transform(pil_img).to(self.device)
        
        if unsqueeze:
            return tensor_img.unsqueeze(0)
       
        return tensor_img
    
    def data_postprocess(self, tensor_img):
        """
        Input
        ---------
            - dtype : tensor
            - shape : (1, 3, 1024, 1024)
            - min max : (-1, 1)
            
        Output
        ---------
            - type : cv2 channel(BGR), numpy
            - shape : (1024, 1024, 3)
            - min max : (0, 255)
        """
        img_arr = tensor_img.squeeze().cpu().numpy().clip(-1,1).transpose([1,2,0])*127.5+127.5
        return img_arr[:,:,::-1]
    
if __name__ == '__main__':
    DB = DeBlurrer()