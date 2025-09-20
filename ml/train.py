import argparse
from pathlib import Path
import os

try:
    from ultralytics import YOLO
except Exception as e:
    YOLO = None

from ml.utils.augmentation import get_train_augmentations
from ml.utils.eval import evaluate_run


def parse_args():
    p = argparse.ArgumentParser(description="Train YOLOv8 for traffic violations")
    p.add_argument("--data", type=str, required=True, help="Path to YOLO data.yaml")
    p.add_argument("--model", type=str, default="yolov8n.pt", help="Base model or checkpoint")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--imgsz", type=int, default=1280)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--project", type=str, default="runs/train")
    p.add_argument("--name", type=str, default="dual-traffic")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def main():
    args = parse_args()
    if YOLO is None:
        raise RuntimeError("ultralytics not available. Install with: pip install ultralytics")

    run_dir = Path(args.project) / args.name
    run_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(args.model)

    # Ultralytics handles most augmentation. Additional ones are configured in data.yaml/hyp.
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        workers=args.workers,
        project=args.project,
        name=args.name,
        seed=args.seed,
        verbose=True,
    )

    metrics = evaluate_run(model, imgsz=args.imgsz)
    (run_dir / "metrics.txt").write_text(str(metrics))

    # Export for inference
    export_path = model.export(format="onnx")
    with open(run_dir / "export.txt", "w") as f:
        f.write(str(export_path))

    print("Training complete. Metrics:", metrics)


if __name__ == "__main__":
    main()
