#!/bin/bash
set -e

IMAGE_NAME=${IMAGE_NAME:-"umramahejabeen/invoice-tracker:latest"}
CONTAINER_NAME="invoice-tracker-app"

docker pull "$IMAGE_NAME"

docker stop "$CONTAINER_NAME" || true
docker rm "$CONTAINER_NAME" || true

docker run -d \
  -p 5000:5000 \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"

docker ps