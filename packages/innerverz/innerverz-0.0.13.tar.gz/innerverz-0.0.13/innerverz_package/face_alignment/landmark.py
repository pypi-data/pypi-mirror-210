from __future__ import division
import numpy as np
import cv2
import onnx
import onnxruntime
import os
import pickle
from .utils import face_align
# from ..data import get_object
from ..utils import check_ckpt_exist, convert_image_type, get_url_id

__all__ = [
    'Landmark',
]

class Landmark:
    def __init__(self, folder_name='face_alignment', ckpt_name='2d106det.onnx',force=False, session=None):
        
        url_id = get_url_id('~/.invz_pack/', folder_name, ckpt_name)
        root  = os.path.join('~/.invz_pack/', folder_name)
        ckpt_path = check_ckpt_exist(root, ckpt_name = ckpt_name, url_id = url_id, force = force)
        assert ckpt_path is not None
        
        self.session = session
        find_sub = False
        find_mul = False
        model = onnx.load(ckpt_path)
        graph = model.graph
        for nid, node in enumerate(graph.node[:8]):
            #print(nid, node.name)
            if node.name.startswith('Sub') or node.name.startswith('_minus'):
                find_sub = True
            if node.name.startswith('Mul') or node.name.startswith('_mul'):
                find_mul = True
            if nid<3 and node.name=='bn_data':
                find_sub = True
                find_mul = True
        if find_sub and find_mul:
            #mxnet arcface model
            input_mean = 0.0
            input_std = 1.0
        else:
            input_mean = 127.5
            input_std = 128.0
        self.input_mean = input_mean
        self.input_std = input_std
        #print('input mean and std:', model_file, self.input_mean, self.input_std)
        if self.session is None:
            self.session = onnxruntime.InferenceSession(ckpt_path, None)
        input_cfg = self.session.get_inputs()[0]
        input_shape = input_cfg.shape
        input_name = input_cfg.name
        self.input_size = tuple(input_shape[2:4][::-1])
        self.input_shape = input_shape
        outputs = self.session.get_outputs()
        output_names = []
        for out in outputs:
            output_names.append(out.name)
        self.input_name = input_name
        self.output_names = output_names
        assert len(self.output_names)==1
        output_shape = outputs[0].shape
        self.require_pose = False
        #print('init output_shape:', output_shape)
        if output_shape[1]==3309:
            self.lmk_dim = 3
            self.lmk_num = 68
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets', 'meanshape_68.pkl'), 'rb') as f: 
                self.mean_lmk = pickle.load(f)
            self.require_pose = True
        else:
            self.lmk_dim = 2
            self.lmk_num = output_shape[1]//self.lmk_dim
        self.taskname = 'landmark_%dd_%d'%(self.lmk_dim, self.lmk_num)

    def prepare(self, ctx_id=0, **kwargs):
        if ctx_id<0:
            self.session.set_providers(['CPUExecutionProvider'])

    def get(self, img, bbox):
        # bbox = face.bbox
        w, h = (bbox[2] - bbox[0]), (bbox[3] - bbox[1])
        center = (bbox[2] + bbox[0]) / 2, (bbox[3] + bbox[1]) / 2
        rotate = 0
        _scale = self.input_size[0]  / (max(w, h)*1.5)
        #print('param:', img.shape, bbox, center, self.input_size, _scale, rotate)
        aimg, M = face_align.transform(img, center, self.input_size[0], _scale, rotate)
        input_size = tuple(aimg.shape[0:2][::-1])
        #assert input_size==self.input_size
        blob = cv2.dnn.blobFromImage(aimg, 1.0/self.input_std, input_size, (self.input_mean, self.input_mean, self.input_mean), swapRB=True)
        pred = self.session.run(self.output_names, {self.input_name : blob})[0][0]
        if pred.shape[0] >= 3000:
            pred = pred.reshape((-1, 3))
        else:
            pred = pred.reshape((-1, 2))
        if self.lmk_num < pred.shape[0]:
            pred = pred[self.lmk_num*-1:,:]
        pred[:, 0:2] += 1
        pred[:, 0:2] *= (self.input_size[0] // 2)
        if pred.shape[1] == 3:
            pred[:, 2] *= (self.input_size[0] // 2)

        IM = cv2.invertAffineTransform(M)
        pred = face_align.trans_points(pred, IM)
        # face[self.taskname] = pred
        # if self.require_pose:
        #     P = transform.estimate_affine_matrix_3d23d(self.mean_lmk, pred)
        #     s, R, t = transform.P2sRt(P)
        #     rx, ry, rz = transform.matrix2angle(R)
        #     pose = np.array( [rx, ry, rz], dtype=np.float32 )
        #     face['pose'] = pose #pitch, yaw, roll
        return pred

if __name__ == '__main__':
    from retina_face import RetinaFace
    from PIL import Image
    input_image = np.array(Image.open('yuna.jpg').convert('RGB'))[:, :, ::-1]
    origin_size = input_image.shape
    RF = RetinaFace()
    bbox, _ = RF.detect(input_image)
    lmk_detector = Landmark()
    landmark = lmk_detector.get(input_image, bbox[0][0:4])
    canvas = np.array(Image.open('yuna.jpg').convert('RGB'))
    
    for coord in landmark:
        canvas = cv2.circle(canvas, (int(coord[0]), int(coord[1])), 4, (0,0,225), -1)
    
    Image.fromarray(canvas.astype(np.uint8)).show()