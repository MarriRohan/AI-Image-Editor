from typing import Dict


def evaluate_run(model, imgsz: int = 1280) -> Dict[str, float]:
    try:
        metrics = model.val(imgsz=imgsz, verbose=False)
        return {
            "mAP50": float(getattr(metrics, 'box', getattr(metrics, 'metrics', [0,0,0,0,0])[0])) if metrics is not None else 0.0
        }
    except Exception:
        return {"mAP50": 0.0}
