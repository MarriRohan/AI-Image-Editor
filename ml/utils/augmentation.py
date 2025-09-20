from typing import Any

try:
    import albumentations as A
    _ALB = True
except Exception:
    _ALB = False


def get_train_augmentations() -> Any:
    if _ALB:
        return A.Compose([
            A.RandomBrightnessContrast(p=0.5),
            A.MotionBlur(p=0.2),
            A.CLAHE(p=0.2),
            A.RandomShadow(p=0.2),
            A.HueSaturationValue(p=0.3),
        ])
    return None
