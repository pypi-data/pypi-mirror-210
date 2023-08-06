import os
import cv2
import numpy as np
from .retina_face import RetinaFace
from .landmark import Landmark
from .graphic_utils import *

class FaceAligner():
    def __init__(self, size = 1024, align_style = 'invz'):
        '''
        algin_style has 2 options  
        
        "ffhq" : algorithm used in FFHQ dataset  
        
        "invz" : algorithm costumed by Innerverz.co    
        
        Methods
        --------
        - get_face
        - detect_lmk
        - align_face_from_5
        - align_face_from_106
        - affine_transform
        '''
        
        self.backbone = RetinaFace()
        self.lmk_detector = Landmark()
        self.size = size
        self.algin_style = align_style
        if self.algin_style == 'ffhq':
            self.index_5 = [38,88,86,52,61]
        else:
            self.index_5 = None
        
    
    def get_face(self, img):
        """
        Input
        ---------
            - dtype : cv2 image
            - shape : (h, w, 3)
            - min max : (0, 255)
            
        Output
        ---------
            - aligned_face
                - dtype : numpy array
                - shape : (size, size, 3)
            - tfm
                - dtype : numpy array
                - shape : (2, 3)
            - tfm_inv
                - dtype : numpy array
                - shape : (2, 3)
            - lms_5
                - dtype : numpy array
                - shape : (5, 2)
            - lms_106
                - dtype : numpy array
                - shape : (106, 2)
            - FaceBool
                - dtype : Bool
        """
        
        # img is numpy array
        if img is None:
            return None, None, None, None, False, None 
        
        #get bounding box and confidence score from retina face
        temp, _ = self.backbone.detect(img)

        if len(temp):
            FaceBool = True
            bbox = temp[0][0:4]
            lms_106 = self.lmk_detector.get(img, bbox)
            if self.align_style == 'ffhq': lms_5 = np.array([lms_106[self.index_5[0]], lms_106[self.index_5[1]], lms_106[self.index_5[2]], lms_106[self.index_5[3]], lms_106[self.index_5[4]]])


            aligned_face, tfm, tfm_inv = self.align_face_from_5(img, lms_5)
            return aligned_face, tfm, tfm_inv, lms_5, FaceBool, lms_106
    
        else :
            return None, None, None, None, False, None, 
    
    def detect_lmk(self, img, target_face_num=0):
        """
        Input
        ---------
            - dtype : cv2 image
            - shape : (h, w, 3)
            - min max : (0, 255)
            
        Output
        ---------
            - FaceBool
                - dtype : Bool
            - lms_106
                - dtype : numpy array
                - shape : (106, 2)
            - lms_5
                - dtype : numpy array
                - shape : (5, 2)
        """
        FaceBool = False
        temp, _ = self.backbone.detect(img)
        
        assert target_face_num < len(temp), 'index is larger than detected face' 
        
        if len(temp):
            FaceBool = True
            bbox = temp[0][0:4]
            lms_106 = self.lmk_detector.get(img, bbox)
            if self.align_style == 'ffhq': lms_5 = np.array([lms_106[self.index_5[0]], lms_106[self.index_5[1]], lms_106[self.index_5[2]], lms_106[self.index_5[3]], lms_106[self.index_5[4]]])

        if FaceBool:
            return FaceBool, lms_106, lms_5

        else:
            return FaceBool, None, None
    
    def align_face_from_5(self, img, lms_5p, size = None) :
        """
        Input
        ---------
            - img
                - dtype : cv2 image
                - shape : (h, w, 3)
                - min max : (0, 255)
            - lms_5
                - dtype : numpy array
                - shape : (5, 2)
            
        Output
        ---------
            - aligned_face
                - dtype : numpy array
                - shape : (size, size, 3)
            - tfm
                - dtype : numpy array
                - shape : (2, 3)
            - tfm_inv
                - dtype : numpy array
                - shape : (2, 3)
        """
        if size == None: size = self.size 
        
        if self.algin_style == 'ffhq':
            eye_left     = lms_5p[0]
            eye_right    = lms_5p[1]
            eye_avg      = (eye_left + eye_right) * 0.5
            eye_to_eye   = eye_right - eye_left
            mouth_left   = lms_5p[3]
            mouth_right  = lms_5p[4]
            mouth_avg    = (mouth_left + mouth_right) * 0.5
            eye_to_mouth = mouth_avg - eye_avg


            x = eye_to_eye - np.flipud(eye_to_mouth) * [-1, 1]
            x /= np.hypot(*x)
            x *= max(np.hypot(*eye_to_eye) * 2.0, np.hypot(*eye_to_mouth) * 1.8)
            y = np.flipud(x) * [-1, 1]
            c = eye_avg + eye_to_mouth * 0.1
            quad = np.stack([c - x - y, c - x + y, c + x + y, c + x - y])

            src_pts = quad 
            ref_pts = np.array(((0, 0), (0, size), (size, size), (size, 0)))
            tfm, tfm_inv = get_similarity_transform_for_cv2(src_pts, ref_pts)
            face_img = cv2.warpAffine(np.array(img), tfm, (size, size), borderMode=None)

            return face_img, tfm, tfm_inv
            
            
    def align_face_from_106(self, img, full_lms, size = None):
        """
        Input
        ---------
            - img
                - dtype : cv2 image
                - shape : (h, w, 3)
                - min max : (0, 255)
            - full_lms
                - dtype : numpy array
                - shape : (106, 2)
            - size
                - dtype : int
            
        Output
        ---------
            - aligned_face
                - dtype : numpy array
                - shape : (size, size, 3)
            - tfm
                - dtype : numpy array
                - shape : (2, 3)
            - tfm_inv
                - dtype : numpy array
                - shape : (2, 3)
        """
        if size == None: size = self.size 
        
        if self.align_style == 'ffhq':
            eye_left     = full_lms[38]
            eye_right    = full_lms[88]
            eye_avg      = (eye_left + eye_right) * 0.5
            eye_to_eye   = eye_right - eye_left
            mouth_left   = full_lms[52]
            mouth_right  = full_lms[61]
            mouth_avg    = (mouth_left + mouth_right) * 0.5
            eye_to_mouth = mouth_avg - eye_avg
            c = eye_avg + eye_to_mouth * 0.1
            
            ##################################################################################################
            x = eye_to_eye - np.flipud(eye_to_mouth) * [-1, 1]
            x /= np.hypot(*x) #x를 단위벡터로 만듦
            x *= max(np.hypot(*eye_to_eye) * 2.0 , np.hypot(*eye_to_mouth) * 1.8) 
            y = np.flipud(x) * [-1, 1] 
            ##################################################################################################    
            quad = np.stack([c - x - y, c - x + y, c + x + y, c + x - y])

            src_pts = quad + 0.01*np.random.rand(4,2)
            ref_pts = np.array(((0, 0), (0, size), (size, size), (size, 0)))
            tfm, tfm_inv = get_similarity_transform_for_cv2(src_pts, ref_pts)
            face_img = cv2.warpAffine(np.array(img), tfm, (size, size), borderMode=None)

            return face_img, tfm, tfm_inv
    
            
        elif self.align_style == 'invz':   
            eye_left     = (full_lms[39] + full_lms[35])*0.5
            eye_right    = (full_lms[89] + full_lms[93])*0.5
            eye_avg      = (eye_left + eye_right) * 0.5
            eye_to_eye   = eye_right - eye_left
            mouth_avg = (full_lms[76] + full_lms[82])*0.5
            eye_to_mouth = (mouth_avg - eye_avg)

            ##################################################################################################
            x = eye_to_eye.copy()
            x /= np.hypot(*x) #x를 단위벡터로 만듦
            x *= max(np.hypot(*eye_to_eye) * 2 , np.hypot(*eye_to_mouth) * 4) 
            y = np.flipud(x) * [-1, 1] 
            ##################################################################################################    
            
            c = full_lms[73]
            quad = np.stack([c - x - y, c - x + y, c + x + y, c + x - y])
            src_pts = quad + 0.01*np.random.rand(4,2)
            ref_pts = np.array(((0, 0), (0, size), (size, size), (size, 0)))
            tfm, tfm_inv = get_similarity_transform_for_cv2(src_pts, ref_pts)
            face_img = cv2.warpAffine(np.array(img), tfm, (size, size), borderMode=None)
            # face_img = cv2.warpAffine(np.array(img), tfm, (size, size), borderMode=cv2.BORDER_REFLECT)
        
            return face_img, tfm, tfm_inv
    
    
    def affine_transform(self, full_lms, tfm):
        """
        Input
        ---------
            - full_lms
                - dtype : numpy array
                - shape : (106, 2)
            - tfm
                - dtype : numpy array
                - shape : (2, 3)
                
        Output
        ---------
            - dtype : numpy array
            - shape : (106, 2)
        """
        constant_term = np.ones((106,1))
        expanded_points = np.concatenate((full_lms, constant_term), axis=-1)
        result = np.matmul(expanded_points, np.transpose(tfm))
        return result