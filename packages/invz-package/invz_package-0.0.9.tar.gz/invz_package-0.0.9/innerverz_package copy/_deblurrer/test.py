packages_path = "."
import sys, PIL, numpy, os, cv2
sys.path.append(packages_path)
from torchvision.transforms.functional import to_tensor
from deblurrer import DeBlurrer
import numpy as np

DB = DeBlurrer()

# img_path = f"{packages_path}/sample_images/ol_aligned.jpg"
img_path = '/media/deep3090/ssd4tb/TalkingHeadPipe/inter_result/2_temp_aligned_face_HDH_tensor.png'
img = PIL.Image.open(img_path).convert("RGB").resize((1024,1024))
img_tensor = to_tensor(img).unsqueeze(0).cuda()*2-1

fake, fake_res, edge = DB(img_tensor) # size: 1024, value range: [-1, 1]

fake = fake.squeeze().detach().cpu().numpy().transpose([1,2,0]).clip(-1,1)
fake_res = fake_res.squeeze().detach().cpu().numpy().transpose([1,2,0]).clip(-1,1)
# fake_res = (127.5+(fake_res-127.5)*10).clip(0,255).astype(np.uint8)
cwd = os.path.dirname(os.path.realpath(__file__))
cv2.imwrite(f"{cwd}/result.jpg", fake*127.5+127.5)
cv2.imwrite(f"{cwd}/result_grid.jpg", np.concatenate([np.array(img), fake*127.5+127.5, (fake+fake_res*2).clip(-1,1)*127.5+127.5, (fake+4*fake_res).clip(-1,1)*127.5+127.5], axis=1))