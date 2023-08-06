import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.transforms import InterpolationMode

from ..utils import get_one_hot, get_convexhull_mask, get_new_label

k = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))

class Data_Process():
    # pil numpy
    def image_pp(self, pil_image, size=512, grayscale=False, normalize=False, batch=True, device='cuda'):
        color = "RGB" if grayscale==False else "L"
        
        # img_size
        _pil_image = pil_image.convert(color)
        image = transforms.Resize(size)(_pil_image)

        # label of not
        image = transforms.ToTensor()(image)            

        if normalize:
            image = image*2-1
        
        if batch:
            image = image.unsqueeze(0)
        
        return image.to(device) #
        
    def label_pp(self, label, mask_type='faceparser', lmk=None, size=512, one_hot=False, batch=True, device='cuda'):
        assert len(label.shape) == 2
        assert mask_type in ['faceparse', 'convexhull']
        
        if mask_type == 'convexhull' and lmk.shape[0] == 106:
            convexhull_mask = get_convexhull_mask(label, lmk)
            label = get_new_label(label, convexhull_mask)
        
        ts_label = torch.tensor(np.array(label)).unsqueeze(0)
        ts_label = transforms.Resize(size, interpolation=InterpolationMode.NEAREST)(ts_label)

        if one_hot:
            ts_label = get_one_hot(ts_label)
        
        if not batch:
            ts_label = torch.reshape(ts_label, (-1,size,size))
            
        return ts_label.to(device)

    def mask_pp(self, mask, dilate_iter=0, erode_iter=0, blur_ksize=13):
        assert len(mask.shape) == 2
        
        if not dilate_iter == 0:
            mask = cv2.dilate(mask.astype(np.float64), k, iterations=dilate_iter)
        elif not erode_iter == 0:
            mask = cv2.erode(np.array(mask).astype(np.float64), k, iterations=erode_iter)
        elif not blur_ksize == 0:
            mask = cv2.blur(np.array(mask).astype(np.float64), (4, 4))
        return mask