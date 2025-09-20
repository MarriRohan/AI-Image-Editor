# Traffic Camera Surveillance & Enforcement System (Duality AI)

End-to-end system for real-time traffic violation detection, license plate OCR, speed estimation, and e-challan workflow. Includes ML training/inference (PyTorch/YOLOv8), FastAPI backend, React web admin UI, and deploy via Docker/Kubernetes.

Monorepo layout:
- ml/ — training, inference, models, datasets, evaluation
- api/ — FastAPI app, routers, auth, DB models, tests
- web/ — React + Tailwind admin UI
- infra/ — Dockerfiles, Kubernetes manifests, Redis/S3 configs
- docs/ — design, API, schema, deploy guide

See docs/deploy_guide.md for setup and deployment.
