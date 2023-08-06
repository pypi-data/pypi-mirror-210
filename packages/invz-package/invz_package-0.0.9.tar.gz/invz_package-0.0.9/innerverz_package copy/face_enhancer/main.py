import os
cwd = os.path.dirname(os.path.realpath(__file__))

import torch
import torch.nn as nn
import numpy as np
from .nets import MyGenerator
from ..utils import check_ckpt_exist, convert_image_type, get_url_id

lmk_indexes = {
    "L_eye" : [33, 35, 36, 37, 39, 40, 41, 42],
    "R_eye" : [87, 89, 90, 91, 93, 94, 95, 96],
    "mouth" : [52, 53, 55, 56, 58, 59, 61, 63, 64, 67, 68, 71]
}


def get_center_coord(lmks, part='L_eye'):
    assert part in lmk_indexes.keys()
    face_part_lmks = []
    for index in lmk_indexes[part]:
        face_part_lmks.append(np.array(lmks[index]))
    face_part_lmks = np.array(face_part_lmks)
    x_lmks, y_lmks = face_part_lmks[:,0], face_part_lmks[:,1]
    x_c, y_c = int(x_lmks.mean()), int(y_lmks.mean()) # sometimes (0,0)
    return x_c, y_c 


def get_grad_mask(size=256):
    x_axis = np.linspace(-1, 1, size)[:, None]
    y_axis = np.linspace(-1, 1, size)[None, :]

    arr1 = np.sqrt(x_axis ** 4 + y_axis ** 4)

    x_axis = np.linspace(-1, 1, size)[:, None]
    y_axis = np.linspace(-1, 1, size)[None, :]

    arr2 = np.sqrt(x_axis ** 2 + y_axis ** 2)

    grad_mask = np.clip(1-(arr1/2+arr2/2), 0, 1)
    return grad_mask


class FaceEnhancer(nn.Module):
    """
    Methods
    ---------
    - forward
        - Input
            - lmks
                - dtype : numpy array
                - shape : (b 106 2)
            - image
                - dtype : tensor
                - shape : (b 3 512 512)
                - min max : (-1 1)
        - Output
            - dtype : tensor
            - shape : (b 3 512 512)
            - min max : (-1 1)
    """
    
    def __init__(self, folder_name='face_enhancer', ckpt_name = 'ckpt.zip', ckpt_face = 'face_090_395k.pt', ckpt_eye = 'eye_012_300k.pt', ckpt_mouth = 'mouth_007_80k.pt', force=False, device = 'cuda'):
        super(FaceEnhancer, self).__init__()

        self.device = device
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root = os.path.join('~/.invz_pack/', folder_name)
        self.dir_folder_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)[:-4]
        
        self.face_enhancer = MyGenerator().to(device)
        self.eye_enhancer = MyGenerator().to(device)
        self.mouth_enhancer = MyGenerator().to(device)
        
        ckpt_pairs = [
            [self.face_enhancer, os.path.join(self.dir_folder_path, ckpt_face)],
            [self.eye_enhancer, os.path.join(self.dir_folder_path, ckpt_eye)],
            [self.mouth_enhancer, os.path.join(self.dir_folder_path, ckpt_mouth)],
        ]
        for enhancer, ckpt_path in ckpt_pairs:
            ckpt = torch.load(os.path.join(cwd, ckpt_path), map_location=device)
            enhancer.load_state_dict(ckpt['model'], strict=False)
            for param in enhancer.parameters():
                param.requires_grad = False
            enhancer.eval()
            del ckpt

        self.grad_mask = torch.from_numpy(get_grad_mask()).to(device)

    def forward(self, lmks, imgs):
        batch_num = imgs.size()[0]

        full_result = self.face_enhancer(imgs) # size: 512, value range: [-1, 1]

        target_R_eye = torch.zeros((batch_num, 3, 256, 256), device='cuda')
        target_L_eye = torch.zeros((batch_num, 3, 256, 256), device='cuda') 
        target_Mouth = torch.zeros((batch_num, 3, 256, 256), device='cuda') 

        for idx in range(batch_num):
            L_xc, L_yc = get_center_coord(lmks[idx], 'L_eye')
            R_xc, R_yc = get_center_coord(lmks[idx], 'R_eye')
            M_xc, M_yc = get_center_coord(lmks[idx], 'mouth')

            target_L_eye[idx] = full_result[idx, :, L_yc-128:L_yc+128, L_xc-128:L_xc+128]
            target_R_eye[idx] = full_result[idx, :, R_yc-128:R_yc+128, R_xc-128:R_xc+128]
            target_Mouth[idx] = full_result[idx, :, M_yc-128:M_yc+128, M_xc-128:M_xc+128]

        L_eye_result = self.eye_enhancer(target_L_eye)
        R_eye_result = self.eye_enhancer(target_R_eye)
        Mouth_result = self.mouth_enhancer(target_Mouth)

        full_result[:, :, L_yc-128:L_yc+128, L_xc-128:L_xc+128] = L_eye_result*self.grad_mask + full_result[:, :, L_yc-128:L_yc+128, L_xc-128:L_xc+128]*(1-self.grad_mask)
        full_result[:, :, R_yc-128:R_yc+128, R_xc-128:R_xc+128] = R_eye_result*self.grad_mask + full_result[:, :, R_yc-128:R_yc+128, R_xc-128:R_xc+128]*(1-self.grad_mask)
        full_result[:, :, M_yc-128:M_yc+128, M_xc-128:M_xc+128] = Mouth_result*self.grad_mask + full_result[:, :, M_yc-128:M_yc+128, M_xc-128:M_xc+128]*(1-self.grad_mask)

        return full_result
