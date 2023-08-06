import torch
import numpy as np
import torch.nn.functional as F

def crop(tensor_image, lmks_68, corp_size=224, scale=1.25):
    c, origin_h, origin_w = tensor_image.size()
    left = torch.min(lmks_68[:,0]); right = torch.max(lmks_68[:,0]); top = torch.min(lmks_68[:,1]); bottom = torch.max(lmks_68[:,1])
    
    old_size = (right - left + bottom - top)/2*1.1
    center = torch.tensor([right - (right - left) / 2.0, bottom - (bottom - top) / 2.0 ])
    new_size = int(old_size*scale) # 얼굴에서 나오는 size
    
    # 좌상, 좌하, 우상, 우하
    lu = torch.tensor([center[0]-new_size/2, center[1]-new_size/2])
    ld = torch.tensor([center[0]-new_size/2, center[1]+new_size/2])
    ru = torch.tensor([center[0]+new_size/2, center[1]-new_size/2])
    rd = torch.tensor([center[0]+new_size/2, center[1]+new_size/2])
    
    min_pad = torch.cat((lu,ld,ru,rd), dim=-1).min()
    max_pad = torch.cat((lu,ld,ru,rd), dim=-1).max() - origin_w
    
    if min_pad < 0 or max_pad > 0:
        pad_amount = int(max(abs(min_pad), abs(max_pad)))
        tensor_image = F.pad(tensor_image.unsqueeze(0), (pad_amount, pad_amount,pad_amount, pad_amount),"constant", 0).squeeze(0)
    
        lu += pad_amount
        ld += pad_amount
        ru += pad_amount
        rd += pad_amount
    
    crop_tensor_image = tensor_image[:, int(lu[1]):int(rd[1]), int(lu[0]):int(rd[0])] # c y x
    resize_crop_tensor_image = F.interpolate(crop_tensor_image.unsqueeze(0), (corp_size, corp_size), mode='bilinear').squeeze(0)
    return resize_crop_tensor_image

def get_crop(batch_image, batch_lmk):
    batch_crop_image = []
    for image, lmk in zip(batch_image, batch_lmk):
        crop_image = crop(image, lmk).clip(-1,1)
        batch_crop_image.append(crop_image * .5 + .5)

    batch_crop_image = torch.stack(batch_crop_image, dim=0)
    return batch_crop_image
