#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./scripts/setup_docker.sh

Build base and run Docker images and start the Agent Zero container via docker compose.

Environment variables:
  A0_BRANCH  Git branch to build (default: main)
  A0_PORT    Host port for the web UI (default: 50080)
  A0_VOLUME  Host directory to mount at /a0 (default: ./docker/run/agent-zero)

Example:
  A0_PORT=50001 A0_BRANCH=development A0_VOLUME="$HOME/agent-zero-data" ./scripts/setup_docker.sh
USAGE
}

# Show help without requiring prerequisites
if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

# prerequisite checks
if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker is required but not installed." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Error: docker compose plugin is required." >&2
  exit 1
fi

# environment variables with defaults
BRANCH="${A0_BRANCH:-main}"
PORT="${A0_PORT:-50080}"
VOLUME="${A0_VOLUME:-$(pwd)/docker/run/agent-zero}"

mkdir -p "$VOLUME"

echo "Building base image..."
docker build --pull -t agent0ai/agent-zero-base:latest docker/base

echo "Building run image for branch '$BRANCH'..."
docker build --pull -t agent0ai/agent-zero:latest --build-arg BRANCH="$BRANCH" docker/run

echo "Starting docker compose..."
export A0_PORT="$PORT" A0_VOLUME="$VOLUME"
(cd docker/run && docker compose up)
