import base64

import cv2
import numpy as np


def _decode_image_file(file_storage) -> np.ndarray | None:
    """
    将上传的文件（FileStorage）转换为 OpenCV 图像（np.ndarray, BGR）
    """
    file_bytes = file_storage.read()
    if not file_bytes:
        return None
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def _encode_image_to_base64(img: np.ndarray) -> str | None:
    """
    将 OpenCV 图像编码为 JPEG，再转成 Base64 字符串
    返回形如 "data:image/jpeg;base64,xxxxxx"
    """
    ok, buf = cv2.imencode(".jpg", img)
    if not ok:
        return None
    b64 = base64.b64encode(buf).decode("utf-8")
    return "data:image/jpeg;base64," + b64


