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

def to_one_hot(mask, size=512): # 0 ~ 8 h w
    mask_ = torch.tensor(mask, dtype=torch.int64)
    c = 19
    # c = np.array(list(face_parsing_converter.values())).max() + 1
    h,w = mask_.size()

    mask_ = torch.reshape(mask_,(1,1,h,w))
    one_hot_mask = torch.zeros(1, c, h, w)
    one_hot_mask_ = one_hot_mask.scatter_(1, mask_, 1.0)
    one_hot_mask_ = F.interpolate(one_hot_mask_, (size, size), mode='nearest')
    return one_hot_mask_