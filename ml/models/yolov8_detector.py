from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict
import time
import numpy as np

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None


@dataclass
class Detection:
    x1: float
    y1: float
    x2: float
    y2: float
    conf: float
    cls_id: int
    cls_name: str
    track_id: Optional[int]
    ts: Optional[float]
    @property
    def w(self): return self.x2 - self.x1
    @property
    def h(self): return self.y2 - self.y1
    @property
    def cx(self): return (self.x1 + self.x2) / 2
    @property
    def cy(self): return (self.y1 + self.y2) / 2


class _NaiveTracker:
    def __init__(self, iou_thr: float = 0.3, max_age: int = 30):
        self.iou_thr = iou_thr
        self.max_age = max_age
        self.tracks: Dict[int, Dict] = {}
        self.next_id = 1

    @staticmethod
    def _iou(a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        inter_x1 = max(ax1, bx1)
        inter_y1 = max(ay1, by1)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)
        inter = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
        area_a = (ax2 - ax1) * (ay2 - ay1)
        area_b = (bx2 - bx1) * (by2 - by1)
        union = area_a + area_b - inter + 1e-6
        return inter / union

    def update(self, boxes: List[List[float]]):
        t = time.time()
        assigned = set()
        # Try to assign existing tracks
        for tid, tr in list(self.tracks.items()):
            tr['age'] += 1
            best = -1
            best_iou = 0.0
            for i, b in enumerate(boxes):
                if i in assigned:
                    continue
                iou = self._iou(tr['box'], b)
                if iou > best_iou:
                    best_iou, best = iou, i
            if best_iou >= self.iou_thr and best >= 0:
                tr['box'] = boxes[best]
                tr['age'] = 0
                tr['ts'] = t
                assigned.add(best)
        # Create new tracks for unassigned detections
        for i, b in enumerate(boxes):
            if i in assigned:
                continue
            self.tracks[self.next_id] = { 'box': b, 'age': 0, 'ts': t }
            self.next_id += 1
        # Remove stale
        for tid in list(self.tracks.keys()):
            if self.tracks[tid]['age'] > self.max_age:
                del self.tracks[tid]
        return self.tracks


class YoloV8Detector:
    def __init__(self, model_path: str = "yolov8n.pt", class_map: Optional[Dict[int,str]] = None, conf: float = 0.25, iou: float = 0.5):
        if YOLO is None:
            raise RuntimeError("ultralytics not available. Install with: pip install ultralytics")
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou
        self.class_map = class_map
        self.tracker = _NaiveTracker()
        self.names = self.model.model.names if hasattr(self.model, 'model') else {}

    def predict(self, bgr_image: np.ndarray) -> List[Detection]:
        res = self.model.predict(source=bgr_image[..., ::-1], verbose=False, conf=self.conf, iou=self.iou)[0]
        boxes = res.boxes.xyxy.cpu().numpy() if res.boxes is not None else np.zeros((0,4))
        confs = res.boxes.conf.cpu().numpy() if res.boxes is not None else np.zeros((0,))
        clss = res.boxes.cls.cpu().numpy().astype(int) if res.boxes is not None else np.zeros((0,), dtype=int)
        tracks = self.tracker.update(boxes.tolist())
        out: List[Detection] = []
        # Map detection index to track id
        track_assign = {}
        for tid, tr in tracks.items():
            track_assign[tuple(map(float, tr['box']))] = (tid, tr['ts'])
        for i in range(len(boxes)):
            x1,y1,x2,y2 = boxes[i]
            key = tuple(map(float, [x1,y1,x2,y2]))
            # Find best match by IoU with track boxes
            best_tid, best_ts, best_iou = None, None, 0.0
            for tbox, (tid, ts) in track_assign.items():
                iou = _NaiveTracker._iou(tbox, [x1,y1,x2,y2])
                if iou > best_iou:
                    best_iou, best_tid, best_ts = iou, tid, ts
            cls_id = int(clss[i])
            name = self.class_map.get(cls_id) if self.class_map else (self.names.get(cls_id, str(cls_id)))
            out.append(Detection(x1=float(x1), y1=float(y1), x2=float(x2), y2=float(y2), conf=float(confs[i]), cls_id=cls_id, cls_name=name, track_id=best_tid, ts=best_ts))
        return out
