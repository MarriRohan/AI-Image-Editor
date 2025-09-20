from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import time
import io
import cv2
import numpy as np

from ml.models.yolov8_detector import YoloV8Detector, Detection
from ml.models.plate_enhancer import enhance_plate_for_ocr

try:
    import easyocr
    _EASYOCR_AVAILABLE = True
except Exception:
    _EASYOCR_AVAILABLE = False

try:
    import pytesseract
    _TESS_AVAILABLE = True
except Exception:
    _TESS_AVAILABLE = False


@dataclass
class Violation:
    type: str
    score: float


@dataclass
class PlateRead:
    text: str
    confidence: float
    crop: np.ndarray


@dataclass
class Evidence:
    frame: np.ndarray
    bboxes: List[Tuple[int, int, int, int]]
    plate_crop: Optional[np.ndarray]
    timestamp_ms: int
    speed_kph: Optional[float]


class InferenceEngine:
    def __init__(self, model_path: str = "yolov8n.pt", class_map: Optional[Dict[int, str]] = None):
        self.detector = YoloV8Detector(model_path=model_path, class_map=class_map)
        self.reader = easyocr.Reader(['en']) if _EASYOCR_AVAILABLE else None

    def _ocr_plate(self, plate_img: np.ndarray) -> Optional[PlateRead]:
        if plate_img is None:
            return None
        proc = enhance_plate_for_ocr(plate_img)
        if self.reader is not None:
            res = self.reader.readtext(proc)
            if res:
                # choose the longest high-conf text
                line = max(res, key=lambda x: x[2])
                return PlateRead(text=line[1], confidence=float(line[2]), crop=proc)
        if _TESS_AVAILABLE:
            txt = pytesseract.image_to_string(proc)
            txt = ''.join([c for c in txt if c.isalnum()]).upper()
            return PlateRead(text=txt, confidence=0.6, crop=proc)
        return None

    def _estimate_speed(self, track_history: List[Tuple[int, int, float]], pixel_per_meter: float, fps: float) -> Optional[float]:
        if len(track_history) < 2 or pixel_per_meter <= 0 or fps <= 0:
            return None
        (x1, y1, t1), (x2, y2, t2) = track_history[-2], track_history[-1]
        dist_pix = float(np.hypot(x2 - x1, y2 - y1))
        dist_m = dist_pix / pixel_per_meter
        dt = max(1e-3, t2 - t1)
        mps = dist_m / dt
        return mps * 3.6

    def process_frame(self, bgr: np.ndarray, timestamp_ms: Optional[int] = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        h, w = bgr.shape[:2]
        now_ms = timestamp_ms if timestamp_ms is not None else int(time.time() * 1000)
        meta = meta or {}
        results = self.detector.predict(bgr)

        violations: List[Violation] = []
        plate_crop = None
        plate_read: Optional[PlateRead] = None
        speed_kph: Optional[float] = None

        # Group detections per track
        tracks: Dict[int, List[Detection]] = {}
        for det in results:
            if det.track_id is None:
                continue
            tracks.setdefault(det.track_id, []).append(det)

        for tid, dets in tracks.items():
            # basic logic: if motorcycle/person and no helmet box around head, flag
            cls_set = {d.cls_name for d in dets}
            conf_avg = float(np.mean([d.conf for d in dets]))

            if ("motorcycle" in cls_set or "bike" in cls_set) and "helmet" not in cls_set:
                violations.append(Violation(type="no_helmet", score=conf_avg))

            if "car" in cls_set and "seatbelt" not in cls_set:
                violations.append(Violation(type="no_seatbelt", score=conf_avg))

            # overspeed via track speed estimate (if geometry provided)
            px_per_m = float(meta.get("pixel_per_meter", 0))
            fps = float(meta.get("fps", 0))
            speed_kph = self._estimate_speed([(int(d.cx), int(d.cy), d.ts) for d in dets if d.ts is not None], px_per_m, fps) or speed_kph

            # red light crossing if crossing a stop-line while signal is red
            if meta.get("signal_state") == "red":
                y_line = int(meta.get("stop_line_y", h - 50))
                crossed = any(d.y2 > y_line for d in dets if d.cls_name in {"car","motorcycle","bus","truck"})
                if crossed:
                    violations.append(Violation(type="red_light_cross", score=conf_avg))

            # license plate crop (heuristic: use smallest wide box labeled plate if present)
            plate_dets = [d for d in dets if d.cls_name in {"license_plate","plate"}]
            if plate_dets:
                plate_det = sorted(plate_dets, key=lambda d: (d.w * d.h))[0]
                x1, y1, x2, y2 = map(int, [plate_det.x1, plate_det.y1, plate_det.x2, plate_det.y2])
                x1, y1, x2, y2 = max(0,x1), max(0,y1), min(w,x2), min(h,y2)
                plate_crop = bgr[y1:y2, x1:x2].copy()
                meta['plate_bbox'] = [x1,y1,x2,y2]

        if plate_crop is not None:
            plate_read = self._ocr_plate(plate_crop)

        boxes = [(int(d.x1), int(d.y1), int(d.x2), int(d.y2)) for d in results]
        ev = Evidence(frame=bgr, bboxes=boxes, plate_crop=plate_crop, timestamp_ms=now_ms, speed_kph=speed_kph)

        out: Dict[str, Any] = {
            "violations": [v.__dict__ for v in violations],
            "plate": plate_read.__dict__ if plate_read else None,
            "evidence": {
                "timestamp_ms": ev.timestamp_ms,
                "speed_kph": ev.speed_kph,
                "bboxes": ev.bboxes,
                "plate_bbox": meta.get("plate_bbox"),
            },
        }
        return out
