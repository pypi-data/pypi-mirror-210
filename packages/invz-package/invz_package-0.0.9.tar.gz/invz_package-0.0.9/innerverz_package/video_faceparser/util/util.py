import torch
import numpy as np
from torch import nn
import torch.nn.functional as F
import numpy as np
from scipy import interpolate
from PIL import Image
from torchvision import transforms
from tqdm import tqdm

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5],std=[0.5,0.5,0.5]),
])

class InputPadder:
    """ Pads images such that dimensions are divisible by 8 """
    def __init__(self, dims, mode='sintel'):
        self.ht, self.wd = dims[-2:]
        pad_ht = (((self.ht // 8) + 1) * 8 - self.ht) % 8
        pad_wd = (((self.wd // 8) + 1) * 8 - self.wd) % 8
        if mode == 'sintel':
            self._pad = [pad_wd//2, pad_wd - pad_wd//2, pad_ht//2, pad_ht - pad_ht//2]
        else:
            self._pad = [pad_wd//2, pad_wd - pad_wd//2, 0, pad_ht]

    def pad(self, *inputs):
        return [F.pad(x, self._pad, mode='replicate') for x in inputs]

    def unpad(self,x):
        ht, wd = x.shape[-2:]
        c = [self._pad[2], ht-self._pad[3], self._pad[0], wd-self._pad[1]]
        return x[..., c[0]:c[1], c[2]:c[3]]

def forward_interpolate(flow):
    flow = flow.detach().cpu().numpy()
    dx, dy = flow[0], flow[1]

    ht, wd = dx.shape
    x0, y0 = np.meshgrid(np.arange(wd), np.arange(ht))

    x1 = x0 + dx
    y1 = y0 + dy
    
    x1 = x1.reshape(-1)
    y1 = y1.reshape(-1)
    dx = dx.reshape(-1)
    dy = dy.reshape(-1)

    valid = (x1 > 0) & (x1 < wd) & (y1 > 0) & (y1 < ht)
    x1 = x1[valid]
    y1 = y1[valid]
    dx = dx[valid]
    dy = dy[valid]

    flow_x = interpolate.griddata(
        (x1, y1), dx, (x0, y0), method='nearest', fill_value=0)

    flow_y = interpolate.griddata(
        (x1, y1), dy, (x0, y0), method='nearest', fill_value=0)

    flow = np.stack([flow_x, flow_y], axis=0)
    return torch.from_numpy(flow).float()


def bilinear_sampler(img, coords, mode='bilinear', mask=False):
    """ Wrapper for grid_sample, uses pixel coordinates """
    H, W = img.shape[-2:]
    xgrid, ygrid = coords.split([1,1], dim=-1)
    xgrid = 2*xgrid/(W-1) - 1
    ygrid = 2*ygrid/(H-1) - 1

    grid = torch.cat([xgrid, ygrid], dim=-1)
    img = F.grid_sample(img, grid, align_corners=True)

    if mask:
        mask = (xgrid > -1) & (ygrid > -1) & (xgrid < 1) & (ygrid < 1)
        return img, mask.float()

    return img


def coords_grid(batch, ht, wd, device):
    coords = torch.meshgrid(torch.arange(ht, device=device), torch.arange(wd, device=device))
    coords = torch.stack(coords[::-1], dim=0).float()
    return coords[None].repeat(batch, 1, 1, 1)


def upflow8(flow, mode='bilinear'):
    new_size = (8 * flow.shape[2], 8 * flow.shape[3])
    return  8 * F.interpolate(flow, size=new_size, mode=mode, align_corners=True)



def get_batch_frames(frame_path_chunk, side_window, size):
    frame_path_chunk = frame_path_chunk[1:side_window+1][::-1] + frame_path_chunk + frame_path_chunk[-side_window-1:-1][::-1]
    
    batch_frames = []
    for frame_path in tqdm(frame_path_chunk):
        batch_frames += [transform(Image.open(frame_path).resize((size,size))).unsqueeze(0).cpu()]
    
    # enlarge frames for more accurate parsing maps and optical flows     
    # batch_frames = torch.cat(batch_frames, dim=0)
    batch_frames = torch.cat(batch_frames, dim=0)
    
    return batch_frames

def get_batch_labels(batch_frames, parsingpredictor, side_window):
    with torch.no_grad():
        batch_labels = parsingpredictor.parsing_net(2*batch_frames.to('cuda')).detach().cpu()
    batch_labels
    
    return batch_labels
    
    

def arrange_mask(parsing, output_size=512):
    Lbrow_mask = torch.where(parsing==2, 1, 0) + torch.where(parsing==3, 1, 0)
    Lbrow_mask[:, :, :output_size//2] = 0
    parsing = Lbrow_mask * 2 + (1 - Lbrow_mask) * parsing

    Rbrow_mask = torch.where(parsing==2, 1, 0) + torch.where(parsing==3, 1, 0)
    Rbrow_mask[:, :, output_size//2:] = 0
    parsing = Rbrow_mask * 3 + (1 - Rbrow_mask) * parsing

    Leye_mask = torch.where(parsing==4, 1, 0) + torch.where(parsing==5, 1, 0)
    Leye_mask[:, :, :output_size//2] = 0
    parsing = Leye_mask * 4 + (1 - Leye_mask) * parsing
    
    Reye_mask = torch.where(parsing==4, 1, 0) + torch.where(parsing==5, 1, 0)
    Reye_mask[:, :, output_size//2:] = 0
    parsing = Reye_mask * 5 + (1 - Reye_mask) * parsing
    
    Leye_mask = torch.where(parsing==7, 1, 0) + torch.where(parsing==8, 1, 0)
    Leye_mask[:, :, :output_size//2] = 0
    parsing = Leye_mask * 7 + (1 - Leye_mask) * parsing
    
    # Reye
    Reye_mask = torch.where(parsing==7, 1, 0) + torch.where(parsing==8, 1, 0)
    Reye_mask[:, :, output_size//2:] = 0
    parsing = Reye_mask * 8 + (1 - Reye_mask) * parsing
    return parsing
    
def get_innerface_mask(numpy_label):
    canvas = np.zeros_like(numpy_label)
    canvas += np.where(numpy_label==1, 1, 0)
    canvas += np.where(numpy_label==2, 1, 0)
    canvas += np.where(numpy_label==3, 1, 0)
    canvas += np.where(numpy_label==4, 1, 0)
    canvas += np.where(numpy_label==5, 1, 0)
    canvas += np.where(numpy_label==6, 1, 0)
    canvas += np.where(numpy_label==10, 1, 0)
    canvas += np.where(numpy_label==11, 1, 0)
    canvas += np.where(numpy_label==12, 1, 0)
    canvas += np.where(numpy_label==13, 1, 0)
    return canvas

def get_list_chunk(lists, n):
    m = len(lists)//n + 1 if len(lists)%n != 0 else len(lists)//n
    return [lists[i:i+m] for i in range(0,len(lists),m)]

# from RAFT
def warp(x, flo):
    """
    warp an image/tensor (im2) back to im1, according to the optical flow
    x: [B, C, H, W] (im2)
    flo: [B, 2, H, W] flow
    """
    B, C, H, W = x.size()
    # mesh grid 
    xx = torch.arange(0, W).view(1,-1).repeat(H,1)
    yy = torch.arange(0, H).view(-1,1).repeat(1,W)
    xx = xx.view(1,1,H,W).repeat(B,1,1,1)
    yy = yy.view(1,1,H,W).repeat(B,1,1,1)
    grid = torch.cat((xx,yy),1).float()


    #x = x.cuda()
    grid = grid.cuda()
    vgrid = grid + flo # B,2,H,W

    # scale grid to [-1,1] 
    ##2019 code
    vgrid[:,0,:,:] = 2.0*vgrid[:,0,:,:].clone()/max(W-1,1)-1.0 
    vgrid[:,1,:,:] = 2.0*vgrid[:,1,:,:].clone()/max(H-1,1)-1.0

    vgrid = vgrid.permute(0,2,3,1)
    output = nn.functional.grid_sample(x, vgrid,align_corners=True)
    mask = torch.autograd.Variable(torch.ones(x.size())).cuda()
    mask = nn.functional.grid_sample(mask, vgrid,align_corners=True)

    ##2019 author
    mask[mask<0.9999] = 0
    mask[mask>0] = 1

     ##2019 code
     # mask = torch.floor(torch.clamp(mask, 0 ,1))

    return output*mask, mask