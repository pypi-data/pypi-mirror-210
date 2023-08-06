import cv2
from PIL import Image

from innerverz_package import Data_Process

DP = Data_Process()

image_path = 'sample.png'
pil_image = Image.open(image_path)
ts_image = DP.image_pp(pil_image, 512, normalize=True)


"""
        face alignment usage
"""
from innerverz_package import FaceAligner
FA = FaceAligner(align_style='ffhq')

cv2_image = cv2.imread(image_path)
aligned_face, tfm, tfm_inv, lms_5, lms_106, face_bool = FA.get_face(cv2_image)

face_bool, lms_106, lms_5 = FA.detect_lmk(cv2_image)

aligned_face, tfm, tfm_inv = FA.align_face_from_5(cv2_image, lms_5)

aligned_lmk = FA.affine_transform(lms_106, tfm)

"""
            Upsampler usage
"""
from innerverz_package import Upsampler
US = Upsampler()
ts_aligned_face = DP.image_pp(aligned_face, 512, normalize=False)
result = US(ts_aligned_face)
_result = DP.vis_pp(result, normalize=False)
