from dataclasses import dataclass
from typing import Optional

@dataclass
class TrafficDatasetConfig:
    data_yaml: str
    imgsz: int = 1280
    batch: int = 16
    workers: int = 8
    epochs: int = 50
    seed: int = 42
