import cv2
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.transforms import InterpolationMode

from ..utils import get_one_hot, get_convexhull_mask, get_new_label, get_part_img, convert_image_type

k = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))

class Data_Process():
    def __init__(self):
        """
        Methods
        --------
        - image_pp
        - label_pp
        - mask_pp
        - faceparts_pp
        - vis_pp
        
        
        """
        return 
        
    # pil numpy
    def image_pp(self, image, size=512, grayscale=False, normalize=False, batch=True, device='cuda'):
        color = "RGB" if grayscale==False else "L"
        
        # img_size
        pil_image = convert_image_type(image, target='pillow')
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
        assert mask_type in ['faceparser', 'convexhull', 'head']
        
        label = convert_image_type(label, target='pillow')
        label = np.array(label.convert('L').resize((size,size), Image.NEAREST))
        
        if mask_type == 'convexhull' and lmk.shape[0] == 106:
            convexhull_mask = get_convexhull_mask(label, lmk)
            label = get_new_label(label, convexhull_mask)
        elif mask_type == 'head':
            label = np.where(label < 14, label, 0) + np.where(label == 17, 17, 0)
        
        ts_label = torch.tensor(label).unsqueeze(0)
        ts_label = transforms.Resize(size, interpolation=InterpolationMode.NEAREST)(ts_label)

        if one_hot:
            ts_label = get_one_hot(ts_label)
        
        if not batch:
            ts_label = torch.reshape(ts_label, (-1,size,size))
        elif batch and len(ts_label.shape) == 3:
            ts_label = ts_label.unsqueeze(0)
            
        return ts_label.to(device)

    def mask_pp(self, mask, dilate_iter=0, erode_iter=0, blur_ksize=0):
        assert len(mask.shape) == 2
        
        if not dilate_iter == 0:
            mask = cv2.dilate(mask.astype(np.float64), k, iterations=dilate_iter)
        elif not erode_iter == 0:
            mask = cv2.erode(np.array(mask).astype(np.float64), k, iterations=erode_iter)
        elif not blur_ksize == 0:
            mask = cv2.blur(np.array(mask).astype(np.float64), (blur_ksize, blur_ksize))
        return mask
    
    
    def faceparts_pp(self, face, lmk, facepart='L_eye'):
        assert facepart in ['L_eye', 'R_eye', 'mouth']
        assert lmk.shape[0] == 106
        
        facepart_img = get_part_img(face, lmk, facepart=facepart)
        return facepart_img
    
    def vis_pp(self, target, normalize=True, color=True):
        if len(target.shape) == 3:
            target = target.squeeze(0).clone().detach().cpu().numpy()
        else:
            target = target.squeeze(0).clone().detach().permute([1,2,0]).cpu().numpy()
        
        if normalize:
            target = target * .5 + .5
            
        if color:
            target = target[:,:,::-1]
            target *= 255
            
        return target