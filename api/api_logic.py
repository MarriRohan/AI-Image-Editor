from pathlib import Path
import os
import cv2
import numpy as np
import requests
from typing import Dict, Any, Optional
from api.models import SessionLocal, ViolationEvent
from api.config import settings
from ml.inference import InferenceEngine

_ENGINE = None

def get_engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = InferenceEngine()
    return _ENGINE


def ensure_dirs():
    Path("data/evidence").mkdir(parents=True, exist_ok=True)


def save_evidence(frame_bgr: np.ndarray, plate_crop: Optional[np.ndarray], event: Dict[str, Any]) -> Dict[str, str]:
    ensure_dirs()
    base = f"evt_{event['evidence']['timestamp_ms']}"
    frame_path = Path("data/evidence") / f"{base}.jpg"
    cv2.imwrite(str(frame_path), frame_bgr)
    plate_path = None
    if plate_crop is not None:
        plate_path = Path("data/evidence") / f"{base}_plate.jpg"
        cv2.imwrite(str(plate_path), plate_crop)
    return {"frame": str(frame_path), "plate": str(plate_path) if plate_path else ""}


def process_frame_and_store(image_bytes: bytes, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    arr = np.frombuffer(image_bytes, np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    engine = get_engine()
    result = engine.process_frame(bgr, meta=meta)

    # persist
    plate_crop = engine._ocr_plate(result.get('plate', {}).get('crop') if result.get('plate') else None)
    # engine.process_frame already enhanced and cropped; retrieve from engine is not trivial here, so re-crop not available.

    paths = save_evidence(bgr, None, result)

    session = SessionLocal()
    try:
        for v in result["violations"]:
            evt = ViolationEvent(
                type=v["type"],
                score=v["score"],
                plate_text=(result["plate"]["text"] if result.get("plate") else None),
                plate_conf=(result["plate"]["confidence"] if result.get("plate") else None),
                speed_kph=result["evidence"].get("speed_kph"),
                evidence_path=paths["frame"],
                evidence_plate_path=paths["plate"],
                meta=result["evidence"],
            )
            session.add(evt)
        session.commit()
    finally:
        session.close()

    return result


def send_e_challan(payload: Dict[str, Any]) -> Dict[str, Any]:
    url = settings.E_CHALLAN_URL
    if not url:
        return {"status": "mock", "payload": payload}
    try:
        r = requests.post(url, json=payload, timeout=5)
        return {"status": "ok", "response": r.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}
