import cv2
import os
import numpy as np
import torch
import torch.nn.functional as F
import glob
import numpy as np
from PIL import Image
import PIL
import torch
from torchvision.transforms.functional import to_tensor
import shutil

def modulate_innerface(target_img, source_img, target_labels, source_labels):
    target_img = target_img.squeeze(0)
    source_img = source_img.squeeze(0)
    target_labels = target_labels[:,1:].sum(1)
    source_labels = source_labels[:,1:].sum(1)
    canvas = torch.zeros_like(target_img)
    for target_label, source_label in zip(target_labels, source_labels):
        target_mean, source_mean = 0, 0
        target_std, source_std = 1, 1
        if target_label.sum() and source_label.sum():
            target_pixels = torch.masked_select(target_img, target_label.bool())
            target_mean = target_pixels.mean()
            target_std = (target_pixels - target_mean).std() # , target_pixels.std()

            source_pixels = torch.masked_select(source_img, source_label.bool())
            source_mean = source_pixels.mean()
            source_std = (source_pixels - source_mean).std() # , target_pixels.std()
        
        edit_target_img = ((target_img - target_mean)/target_std) * source_std + source_mean
        
        canvas += edit_target_img * target_label
    
    return canvas.unsqueeze(0)

def modulate(target_img, source_img, target_labels, source_labels, skin_mean, skin_std, others_mean, others_std):
    target_img = target_img.squeeze(0)
    source_img = source_img.squeeze(0)
    target_labels = target_labels.squeeze(0)
    source_labels = source_labels.squeeze(0)
    
    # new skin(skin + nose + brow + eye + ear)
    target_labels[1, :, :] = (target_labels[1,:,:] + target_labels[2,:,:] + target_labels[3,:,:] + target_labels[4,:,:] + target_labels[5,:,:]\
         + target_labels[6,:,:] + target_labels[7,:,:] + target_labels[8,:,:] + target_labels[9,:,:] + target_labels[10,:,:]).clip(0,1)
    target_labels[2:11, :, :] *= 0
    
    source_labels[1, :, :] = (source_labels[1,:,:] + source_labels[2,:,:] + source_labels[3,:,:] + source_labels[4,:,:] + source_labels[5,:,:]\
        + source_labels[6,:,:] + source_labels[7,:,:] + source_labels[8,:,:] + source_labels[9,:,:] + source_labels[10,:,:]).clip(0,1)
    source_labels[2:11, :, :] *= 0
    
    # new lips(u lip + d lip)
    target_labels[12, :, :] = (target_labels[12,:,:] + target_labels[13,:,:] + target_labels[11,:,:]).clip(0,1)
    target_labels[13, :, :] *= 0
    target_labels[11, :, :] *= 0
    
    source_labels[12, :, :] = (source_labels[12,:,:] + source_labels[13,:,:] + source_labels[11,:,:]).clip(0,1)
    source_labels[13, :, :] *= 0
    source_labels[11, :, :] *= 0
    
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
            
            if idx == 0:
                edit_target_img = ((target_img - target_mean)/target_std)*source_std*skin_std + source_mean + skin_mean
                # edit_target_img = ((target_img - target_mean)/target_std)*source_std*.7 + source_mean + 0.2
            else:
                edit_target_img = ((target_img - target_mean)/target_std)*source_std*others_std + source_mean + others_mean
                # edit_target_img = ((target_img - target_mean)/target_std)*source_std*.7 + source_mean
                
            # if idx in [11, 12, 13]:
            #     target_label = target_label.cpu().numpy()[:,:,None]
            #     target_label = cv2.blur(target_label, (45, 45))
            #     target_label = torch.tensor(target_label, device='cuda').squeeze()
            blur_target_label = cv2.blur(np.array(target_label)[:,:,None], (13,13))
            canvas += edit_target_img * blur_target_label
    return canvas.unsqueeze(0)

# def modulate(target_img, source_img, target_labels, source_labels):
#     target_img = target_img.squeeze(0)
#     source_img = source_img.squeeze(0)
#     target_labels = target_labels.squeeze(0)
#     source_labels = source_labels.squeeze(0)
    
#     # nose + skin
#     target_labels[1, :, :] = target_labels[1,:,:] + target_labels[10,:,:]
#     target_labels[10, :, :] *= 0
    
#     source_labels[1, :, :] = source_labels[1,:,:] + source_labels[10,:,:]
#     source_labels[10, :, :] *= 0
    
#     canvas = torch.zeros_like(target_img)
#     for idx, (target_label, source_label) in enumerate(zip(target_labels[1:], source_labels[1:])):
#         target_mean, source_mean = 0, 0
#         target_std, source_std = 1, 1
#         if target_label.sum() and source_label.sum():
#             target_pixels = torch.masked_select(target_img, target_label.bool())
#             target_mean = target_pixels.mean()
#             target_std = (target_pixels - target_mean).std() # , target_pixels.std()

#             source_pixels = torch.masked_select(source_img, source_label.bool())
#             source_mean = source_pixels.mean()
#             source_std = (source_pixels - source_mean).std() # , target_pixels.std()
        
#         # if target_labels.shape[0] - 1 == idx:
#         #     import pdb;pdb.set_trace()
#         edit_target_img = ((target_img - target_mean)/target_std)*source_std + source_mean
#         # if idx in [11, 12, 13]:
#         #     target_label = target_label.cpu().numpy()[:,:,None]
#         #     target_label = cv2.blur(target_label, (45, 45))
#         #     target_label = torch.tensor(target_label, device='cuda').squeeze()
#         canvas += edit_target_img * target_label
    
#     return canvas.unsqueeze(0)

def to_one_hot(mask): # 0 ~ 8 h w
    mask_ = torch.tensor(mask, dtype=torch.int64)
    c = 19
    # c = np.array(list(face_parsing_converter.values())).max() + 1
    h,w = mask_.size()

    mask_ = torch.reshape(mask_,(1,1,h,w))
    one_hot_mask = torch.zeros(1, c, h, w)
    one_hot_mask_ = one_hot_mask.scatter_(1, mask_, 1.0)
    one_hot_mask_ = F.interpolate(one_hot_mask_, (h,w), mode='nearest')
    return one_hot_mask_

kernel = np.ones((3, 3), np.uint8)

def get_name_from_path(path):
    base_name = os.path.basename(path)
    frame_name, ext = os.path.splitext(base_name)
    return frame_name


def get_path_list(dir, sorting=True):
    if sorting:
        path_list = sorted(glob.glob(os.path.join(dir,'*.*')))
    else:
        path_list = glob.glob(os.path.join(dir,'*.*'))
        
    return path_list


def expand_and_transform_affine(points, affine_mat):
    constant_term = np.ones((106,1))
    expanded_points = np.concatenate((points, constant_term), axis=1)
    result = np.matmul(expanded_points, np.transpose(affine_mat))
    return result


def parse_list_to_batch(target_list, batch_size):
    batch_list = list(target_list[i:i+batch_size] for i in range(0, len(target_list), batch_size))
    return batch_list


def tensor_to_nparr(tensor, from_0=True):
    if from_0:
        numpy_255 = tensor.clone().detach().cpu().numpy().transpose([1,2,0]).clip(0,1)*255 
    else:
        numpy_255 = tensor.clone().detach().cpu().numpy().transpose([1,2,0]).clip(-1,1)*127.5+127.5
    
    return numpy_255
 
 
def label_to_mask_pair(np_label, size, kernel=kernel):
        np_label = np.where(np_label==8,1,np_label)
        np_label = np.where(np_label==7,1,np_label)
        
        # L_brow + R_brow
        np_label = np.where(np_label==3,2,np_label)
        # L_eye + R_eye
        np_label = np.where(np_label==5,4,np_label)
        # u_lip + d_lip + mouth(11)
        np_label = np.where(np_label==13,12,np_label)
        # np_label = np.where(np_label==11,12,np_label)
        
        
        innerface_mask = np.clip(np.where(np_label <= 13, 1, 0) - np.where(np_label == 0, 1, 0), 0, 1)
        dilation_mask = cv2.dilate(innerface_mask.astype(np.float32), kernel, iterations=25)
        boundary_mask = torch.tensor(dilation_mask - innerface_mask).view(1, 1, size, size)
        
        new_innerface_label = np_label * innerface_mask
        innerface_mask = torch.tensor(innerface_mask).view(1, 1, size, size)

        innerface_mask = torch.tensor(innerface_mask).view(1, 1, size, size)
        return innerface_mask, boundary_mask


def get_to_do(working_dir, standard_dir):
    working_len = len(get_path_list(working_dir, False)) 
    standard_len = len(get_path_list(standard_dir, False))
    
    if working_len == standard_len:
        return False
    
    else:
        return True
  
  
def spawn_forder(dir):
    num = len(os.listdir(dir))
    forder_name = str(num).zfill(4)
    new_forder_name = os.path.join(dir, forder_name)
    try:
        os.makedirs(new_forder_name)
        return new_forder_name
    
    except:
        raise Exception("폴더트리 꼬인듯?")
    
      
def find_lagacy(keyword, work_dir, root_work_dir):
    found_dir = glob.glob(os.path.join(root_work_dir, "*", keyword))
    if len(found_dir):
        for lagacy_dir in found_dir:
            if len(get_path_list(lagacy_dir)):
                return True, lagacy_dir

    return False, None
    
    
class Image_Probe():
    def __init__(self, object):
        self.object = object
        self.detect_type()
    
    def detect_type(self):
        if isinstance(self.object, PIL.Image.Image):
            self.data_type = 'pil'
            
        elif isinstance(self.object, np.ndarray):
            self.data_type = 'arr'
            
        elif isinstance(self.object, torch.Tensor):
            self.data_type = 'tensor'
            
        else:
            Exception(f"{self.save_name} 으로 저장하려는 객체는 이미지로 변환할 수 없습니다.")
        
    def visualize(self, path):
        if self.data_type == 'pil':
            self.object.save(path)
        
        if self.data_type == 'arr':
            Image.fromarray(self.object.astype(np.uint8)).save(path)
        
        if self.data_type == 'tensor':
            # print(type(list(self.object.size())))
            if len(list(self.object.size())) == 4:
                ch3_tensor = self.object[0]
            else: 
                ch3_tensor = self.object
        
            arr = ch3_tensor.cpu().clone().detach().numpy().transpose([1,2,0])*127.5+127.5
            cv2.imwrite(path, arr.astype(np.uint8))
            # Image.fromarray(arr.astype(np.uint8)).save(path)
            
            

"""
Label
"""            
def get_one_hot(mask): # 0 ~ 8 h w
    mask_ = torch.tensor(mask, dtype=torch.int64)
    c = 19
    if len(mask.shape) == 3:
        mask_ = mask_.unsqueeze(0)
    _,_,h,w = mask_.size()

    mask_ = torch.reshape(mask_,(1,1,h,w))
    one_hot_mask = torch.zeros((1, c, h, w), device=mask.device)
    one_hot_mask_ = one_hot_mask.scatter_(1, mask_, 1.0)
    return one_hot_mask_


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

def get_convexhull_mask(pil_label, lmk):
    cv2_face = np.array(pil_label)
    canvas = np.zeros_like(cv2_face).astype(np.uint8)
    points = np.array([lmk[1], lmk[9], lmk[10], lmk[11], lmk[12], lmk[13], lmk[14], lmk[15], lmk[16], lmk[2], lmk[3], lmk[4], lmk[5], lmk[6], lmk[7], lmk[8], lmk[0], lmk[24], lmk[23], lmk[22], lmk[21], lmk[20], lmk[19], lmk[18], lmk[32], lmk[31], lmk[30], lmk[29], lmk[28], lmk[27], lmk[26], lmk[25], lmk[17], lmk[105], lmk[104], lmk[49], lmk[48]], np.int32)
    skin_mask = cv2.fillConvexPoly(canvas, points=points, color=(1,1,1))
    dilation_skin_mask = cv2.dilate(skin_mask, kernel, iterations=15)
    return dilation_skin_mask

def get_new_label(label, convexhull_mask):
    new_label = convexhull_mask * np.where(label==1,1,0) # skin and region
    new_label = new_label * (1 - np.where(label==2,1,0)) + np.where(label==2,1,0) * 2 # Lbrow
    new_label = new_label * (1 - np.where(label==3,1,0)) + np.where(label==3,1,0) * 3 # Rbrow
    new_label = new_label * (1 - np.where(label==4,1,0)) + np.where(label==4,1,0) * 4 # Leye
    new_label = new_label * (1 - np.where(label==5,1,0)) + np.where(label==5,1,0) * 5 # Reye
    new_label = new_label * (1 - np.where(label==6,1,0)) + np.where(label==6,1,0) * 6 # glasses
    new_label = new_label * (1 - np.where(label==10,1,0)) + np.where(label==10,1,0) * 10 # nose
    new_label = new_label * (1 - np.where(label==11,1,0)) + np.where(label==11,1,0) * 11 # mouth
    new_label = new_label * (1 - np.where(label==12,1,0)) + np.where(label==12,1,0) * 12 # ulips
    new_label = new_label * (1 - np.where(label==13,1,0)) + np.where(label==13,1,0) * 13 # dlips
    new_label = new_label * (1 - np.where(label==17,1,0)) # sub hair
    return new_label

    
"""
Face part
"""

facepart_lmk_indexes = {
    "L_eye" : [33, 35, 36, 37, 39, 40, 41, 42],
    "R_eye" : [87, 89, 90, 91, 93, 94, 95, 96],
    "mouth" : [52, 53, 55, 56, 58, 59, 61, 63, 64, 67, 68, 71]
}

def get_center_coord(lmks, part='L_eye'):
    assert part in facepart_lmk_indexes.keys()
    face_part_lmks = []
    for index in facepart_lmk_indexes[part]:
        face_part_lmks.append(np.array(lmks[index]))
    face_part_lmks = np.array(face_part_lmks)
    x_lmks, y_lmks = face_part_lmks[:,0], face_part_lmks[:,1]
    x_min, x_max = int(x_lmks.min()), int(x_lmks.max())
    y_min, y_max = int(y_lmks.min()), int(y_lmks.max())
    x_c, y_c = int(x_lmks.mean()), int(y_lmks.mean()) # sometimes (0,0)
    max_val = max(int(x_max - x_min), int(y_max - y_min))
    W, H = max_val, max_val
    
    return x_c, y_c, W, H


def get_part_img(aligned_face_512, aligned_lmk106, facepart, margin=16):
    x_c, y_c, W, H = get_center_coord(aligned_lmk106, facepart)

    crop_img = aligned_face_512[max(y_c-H//2-margin//2,0):min(y_c+H//2+margin//2,512), max(x_c-W//2-margin//2,0):min(x_c+W//2+margin//2, 512)]
    crop_img = np.array(crop_img, dtype=np.uint8)
    crop_img = cv2.resize(crop_img, (256,256))

    return crop_img

def get_grad_mask(size=256):
    x_axis = np.linspace(-1, 1, size)[:, None]
    y_axis = np.linspace(-1, 1, size)[None, :]

    arr1 = np.sqrt(x_axis ** 4 + y_axis ** 4)

    x_axis = np.linspace(-1, 1, size)[:, None]
    y_axis = np.linspace(-1, 1, size)[None, :]

    arr2 = np.sqrt(x_axis ** 2 + y_axis ** 2)

    grad_mask = np.clip(1-(arr1/2+arr2/2), 0, 1)
    return grad_mask
