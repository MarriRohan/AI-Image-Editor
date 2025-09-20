import cv2
import numpy as np


def _unsharp_mask(img: np.ndarray, ksize=(5,5), amount=1.5, threshold=0) -> np.ndarray:
    blur = cv2.GaussianBlur(img, ksize, 0)
    sharp = cv2.addWeighted(img, 1 + amount, blur, -amount, 0)
    if threshold > 0:
        low_contrast_mask = np.absolute(img - blur) < threshold
        np.copyto(sharp, img, where=low_contrast_mask)
    return sharp


def enhance_plate_for_ocr(plate_bgr: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(plate_bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    den = cv2.fastNlMeansDenoising(gray, None, 15, 7, 21)
    sharp = _unsharp_mask(den, (3,3), amount=1.2)
    eq = cv2.equalizeHist(sharp)
    result = cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR)
    return result
