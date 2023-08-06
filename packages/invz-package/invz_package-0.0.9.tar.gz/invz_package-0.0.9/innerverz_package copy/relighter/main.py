import os
import sys
sys.path.append('../')
cwd = os.path.dirname(os.path.realpath(__file__))

import cv2
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F

import torchvision.transforms as transforms

from .nets import MyGenerator
# from utils.util import crop

from invz_pack.id_extractor import IdExtractor
IE = IdExtractor()

from invz_pack.face_parser import FaceParser
FP = FaceParser()

from torchvision.transforms.functional import to_tensor, rgb_to_grayscale
from ..utils import check_ckpt_exist, convert_image_type, get_url_id


class ReLighter(nn.Module):
    def __init__(self, folder_name='relighter', ckpt_name = 'G_129k.pt', force=False, device = 'cuda'):
        super(ReLighter, self).__init__()
        
        self.device = device
        self.img_size = 512
        self.generator = MyGenerator().to(self.device)
        
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        
        ckpt = torch.load(os.path.join(ckpt_path), map_location=self.device)
        self.generator.load_state_dict(ckpt['model'])
        for param in self.generator.parameters():
            param.requires_grad = False
        self.generator.eval()
        del ckpt
        
        self.tf_gray = transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize((0.5), (0.5))
        ])
        
        self.tf_color_jit = transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            # transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(0.5, 0.5, 0.5, 0.5),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        
        self.tf_color = transforms.Compose([
            transforms.Resize((self.img_size, self.img_size)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        self.kernel = np.ones((3, 3), np.uint8)
        

    def data_preprocess(self, image_path, label_path=None, id_path=None, deca_param_folder_path=None, lmk=None):
        PIL_gray_image = Image.open(image_path).convert("L")
        gray_image = self.tf_gray(PIL_gray_image).unsqueeze(0).cuda()
        
        PIL_color_image = Image.open(image_path)
        color_image = self.tf_color(PIL_color_image).unsqueeze(0).cuda()
        # color_image_jit_gray = self.tf_color_jit(PIL_color_image).mean(0).unsqueeze(0).cuda()
        
        # label
        mask = np.where(np.array(Image.open(label_path))!=0,1,0)
        _mask = F.interpolate(torch.tensor(mask).unsqueeze(0).unsqueeze(0).cuda().type(torch.float32), (self.img_size,self.img_size))
        
        masked_gray_image = _mask * gray_image
        
        # id(gray scale face)
        if id_path == None:
            
            masked_color_image = F.interpolate((color_image * _mask), (256,256))
            id_param = IE(masked_color_image)
            
        else:
            id_param = torch.tensor(np.load(id_path)).cuda()
        
        """
        DECA params
        code_dict.keys() = ['shape', 'tex', 'exp', 'pose', 'cam', 'light']
        orig_visdict.keys() = ['inputs','shape_images','shape_detail_images']
        """
        #@# gray to color
        if deca_param_folder_path == None:
            image = np.array(Image.open(image_path).convert('L'))[:, :, None].repeat(3, axis=2)
            # image_dict = deca.data_preprocess(image_path)
            image_dict = deca.data_preprocess(image_path, image, lmk=lmk)
            code_dict = deca.encode(image_dict['image'][None,...])
        else:
            image_dict, code_dict = {}, {}
            image_dict['tform'] = torch.tensor(np.load(os.path.join(deca_param_folder_path, 'tform.npy'))).cuda()
            image_dict['original_image'] = masked_gray_image
            code_dict['tex'] = torch.tensor(np.load(os.path.join(deca_param_folder_path, 'tex.npy'))).cuda()
            code_dict['exp'] = torch.tensor(np.load(os.path.join(deca_param_folder_path, 'exp.npy'))).cuda()
            code_dict['pose'] = torch.tensor(np.load(os.path.join(deca_param_folder_path, 'pose.npy'))).cuda()
            code_dict['cam'] = torch.tensor(np.load(os.path.join(deca_param_folder_path, 'cam.npy'))).cuda()
            code_dict['light'] = torch.tensor(np.load(os.path.join(deca_param_folder_path, 'light.npy'))).cuda()
            code_dict['images'] = masked_gray_image.repeat(1,3,1,1) * .5 + .5

        # masked_gray_image = torch.ones_like(masked_gray_image) * masked_gray_image
        
        return masked_gray_image, gray_image, _mask, id_param, image_dict, code_dict
        
    # source light -> target light
    def relight(self, source_code_dict, target_code_dict, target_image_dict, target_id_param):
        target_code_dict['light'] = source_code_dict['light']
        
        tform = target_image_dict['tform'][None, ...]
        tform = torch.inverse(tform).transpose(1,2)
        vis_dict = deca.decode(target_code_dict, original_image=target_image_dict['original_image'][None, ...] ,tform=tform)
        relight_detail_shape = rgb_to_grayscale((F.interpolate(vis_dict['shape_detail_images'], (512,512), mode='bilinear') - .5) * 2, num_output_channels=1)

        target_params = torch.cat((target_code_dict['light'].view(1, -1), target_code_dict['cam'].view(1, -1), target_code_dict['pose'].view(1, -1), target_code_dict['detail'].view(1, -1), target_id_param), dim=-1)
        return target_params, relight_detail_shape
    
    
    def forward(self, target_masked_gray_face, detail_shape ,params):
        res = self.generator(target_masked_gray_face, detail_shape ,params)
        result = (res + target_masked_gray_face).clip(-1,1)
        return result, res
        
    def data_postprocess(self, tensor_image):
        tensor_image = F.interpolate(tensor_image, (self.img_size, self.img_size))
        cv2_image = ((tensor_image.clone().detach().squeeze().permute([1,2,0]).cpu().numpy()[:,:,::-1]*.5+.5)*255)
        return cv2_image
