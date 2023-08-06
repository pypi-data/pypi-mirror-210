import sys
import numpy as np
from skimage import color
import torch
import torch.nn.functional as F

###### loss functions ######
def feature_normalize(feature_in):
    feature_in_norm = torch.norm(feature_in, 2, 1, keepdim=True) + sys.float_info.epsilon
    feature_in_norm = torch.div(feature_in, feature_in_norm)
    return feature_in_norm

def to_one_hot(mask): # 0 ~ 8 h w
    mask_ = torch.tensor(mask, dtype=torch.int64)
    c = 19
    # c = np.array(list(face_parsing_converter.values())).max() + 1
    h,w = mask_.size()[0],mask_.size()[1]

    mask_ = torch.reshape(mask_,(1,1,h,w))
    one_hot_mask = torch.zeros(1, c, h, w)
    one_hot_mask_ = one_hot_mask.scatter_(1, mask_, 1.0)
    one_hot_mask_ = F.interpolate(one_hot_mask_, (h,w), mode='nearest')
    return one_hot_mask_

import cv2

def modulate(target_img, source_img, target_labels, source_labels):
    target_img = target_img.squeeze(0)
    source_img = source_img.squeeze(0)
    target_labels = target_labels.squeeze(0)
    source_labels = source_labels.squeeze(0)
    
    # new skin(skin + nose + brow + eye + ear)
    target_labels[1, :, :] = target_labels[1,:,:] + target_labels[2,:,:] + target_labels[3,:,:] + target_labels[4,:,:] + target_labels[5,:,:]\
         + target_labels[6,:,:] + target_labels[7,:,:] + target_labels[8,:,:] + target_labels[9,:,:] + target_labels[10,:,:]
    target_labels[2:11, :, :] *= 0
    
    source_labels[1, :, :] = source_labels[1,:,:] + source_labels[2,:,:] + source_labels[3,:,:] + source_labels[4,:,:] + source_labels[5,:,:]\
        + source_labels[6,:,:] + source_labels[7,:,:] + source_labels[8,:,:] + source_labels[9,:,:] + source_labels[10,:,:]
    source_labels[2:11, :, :] *= 0
    
    # new lips(u lip + d lip)
    target_labels[12, :, :] = target_labels[12,:,:] + target_labels[13,:,:]
    target_labels[13, :, :] *= 0
    
    source_labels[12, :, :] = source_labels[12,:,:] + source_labels[13,:,:]
    source_labels[13, :, :] *= 0
    
    # mouth
    
    
    canvas = torch.zeros_like(target_img)
    for idx, (target_label, source_label) in enumerate(zip(target_labels[1:], source_labels[1:])):
        target_mean, source_mean = 0, 0
        target_std, source_std = 1, 1
        if target_label.sum() and source_label.sum():
            target_pixels = torch.masked_select(target_img, target_label.bool())
            target_mean = target_pixels.mean()
            target_std = (target_pixels - target_mean).std() # , target_pixels.std()

            source_pixels = torch.masked_select(source_img, source_label.bool())
            source_mean = source_pixels.mean()
            source_std = (source_pixels - source_mean).std() # , target_pixels.std()
        
            # if target_labels.shape[0] - 1 == idx:
            #     import pdb;pdb.set_trace()
            edit_target_img = ((target_img - target_mean)/target_std)*source_std + source_mean
            # if idx in [11, 12, 13]:
            #     target_label = target_label.cpu().numpy()[:,:,None]
            #     target_label = cv2.blur(target_label, (45, 45))
            #     target_label = torch.tensor(target_label, device='cuda').squeeze()
            blur_target_label = cv2.blur(np.array(target_label)[:,:,None], (13,13))
            canvas += edit_target_img * blur_target_label
    return canvas.unsqueeze(0)