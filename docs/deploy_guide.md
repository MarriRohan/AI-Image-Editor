# Deployment Guide

Local (API):
- docker build -f infra/docker/Dockerfile.api -t duality/api:latest .
- docker run --rm -p 8000:8000 -v $(pwd)/data:/app/data duality/api:latest

Kubernetes:
- kubectl apply -f infra/k8s/deploy.yaml
- kubectl apply -f infra/k8s/ingress.yaml

GPU Inference:
- Use infra/docker/Dockerfile.ml as base for GPU workers.
