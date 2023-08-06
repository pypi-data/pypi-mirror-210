packages_path = "."
import sys, os, cv2, glob
from PIL import Image
sys.path.append(packages_path)
from torchvision.transforms.functional import to_tensor
import numpy as np
import torch.nn.functional as F
import torch
cwd = os.path.dirname(os.path.realpath(__file__))

from face_enhancer_updated import FaceEnhancer
FE1 = FaceEnhancer(face_ckpt_path='ckpt/face_090_395k.pt', eye_ckpt_path='ckpt/eye_011_300k.pt', mouth_ckpt_path='ckpt/mouth_007_80k.pt')
FE2 = FaceEnhancer(face_ckpt_path='ckpt/face_090_395k.pt', eye_ckpt_path='ckpt/eye_012_300k.pt', mouth_ckpt_path='ckpt/mouth_007_80k.pt')

from innerverz_package import FaceAligner
FA = FaceAligner()

save_root = 'face_enhancer_updated/results_compare'
os.makedirs(save_root, exist_ok=True)
img_paths = glob.glob('./face_enhancer_updated/test_images/*.*')
for img_path in img_paths:
    img = cv2.imread(img_path)
    lmk = FA.detect_lmk(img)[1] # 106 lmks
    aligned_face = FA.get_face(img)[0]

    if lmk is None:
        continue

    img = Image.open(img_path).convert("RGB").resize((1024,1024))
    img_tensor = to_tensor(img).unsqueeze(0).cuda()*2-1

    outputs1 = FE1(to_tensor(lmk), img_tensor)
    outputs2 = FE2(to_tensor(lmk), img_tensor)
    outputs_np1 = outputs1.detach().cpu().numpy().transpose([0, 2, 3, 1]).clip(-1, 1) * 127.5 + 127.5
    outputs_np2 = outputs2.detach().cpu().numpy().transpose([0, 2, 3, 1]).clip(-1, 1) * 127.5 + 127.5
    cv2.imwrite(f'{save_root}/{os.path.basename(img_path)}', np.concatenate([aligned_face, outputs_np1[0][:, :, ::-1], outputs_np2[0][:, :, ::-1]], axis=1))
