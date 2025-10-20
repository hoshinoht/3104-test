#!/usr/bin/env bash
set -euo pipefail

# docker.sh - build and run a small Docker image for a Python script
# Usage: ./docker.sh path/to/script.py [image_name] [container_name]
# If image_name is omitted it'll be derived from the script file name.

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 path/to/script.py [image_name] [container_name]" >&2
  exit 2
fi

SCRIPT_PATH="$1"
if [ ! -f "$SCRIPT_PATH" ]; then
  echo "File not found: $SCRIPT_PATH" >&2
  exit 3
fi

SCRIPT_FILE="$(basename "$SCRIPT_PATH")"
BASE_NAME="${SCRIPT_FILE%.*}"
IMAGE_NAME="${2:-${BASE_NAME}:latest}"
CONTAINER_NAME="${3:-${BASE_NAME}-container}"

# check docker CLI
if ! command -v docker >/dev/null 2>&1; then
  echo "docker CLI not found. Please install Docker and ensure it's in your PATH." >&2
  exit 4
fi

BUILD_DIR="$(mktemp -d /tmp/docker-build-XXXX)"
cleanup() {
  rm -rf "$BUILD_DIR"
}
trap cleanup EXIT


if [ -f Dockerfile ]; then
  echo "Repository Dockerfile found. Building image $IMAGE_NAME from project root."
  docker build -t "$IMAGE_NAME" .
else
  echo "Creating build context in $BUILD_DIR"

  # Copy the script and any local modules (simple approach: copy the whole repo root's python files if they are nearby)
  cp "$SCRIPT_PATH" "$BUILD_DIR/"

  # If there's a requirements.txt in the repo root, copy it
  if [ -f "requirements.txt" ]; then
    cp requirements.txt "$BUILD_DIR/"
  fi

  # Create Dockerfile
  cat > "$BUILD_DIR/Dockerfile" <<EOF
FROM python:3.10-slim

WORKDIR /app

# If the user provided a requirements.txt, install from it; otherwise install grpcio and grpcio-tools
COPY requirements.txt ./
RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    else \
      pip install --no-cache-dir grpcio grpcio-tools; \
    fi

COPY $SCRIPT_FILE ./

EXPOSE 50051

CMD ["python", "$SCRIPT_FILE"]
EOF

  echo "Dockerfile generated:" 
  sed -n '1,200p' "$BUILD_DIR/Dockerfile"

  echo "Building image $IMAGE_NAME ..."
  docker build -t "$IMAGE_NAME" "$BUILD_DIR"
fi

# If a container with the same name exists, stop and remove it
if docker ps -a --format '{{.Names}}' | grep -xq "$CONTAINER_NAME"; then
  echo "Stopping and removing existing container $CONTAINER_NAME"
  docker rm -f "$CONTAINER_NAME" >/dev/null || true
fi

echo "Running container $CONTAINER_NAME (mapping port 50051)"
docker run -d --name "$CONTAINER_NAME" -p 50051:50051 "$IMAGE_NAME"

echo "Container started. To view logs: docker logs -f $CONTAINER_NAME"
echo "To stop and remove: docker rm -f $CONTAINER_NAME"
