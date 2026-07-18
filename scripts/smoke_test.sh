#!/bin/bash
set -e

APP_URL=${APP_URL:-"http://localhost:5000"}

for i in {1..10}
do
  if curl -f "$APP_URL/health"; then
    echo "Smoke test passed"
    exit 0
  fi

  echo "Waiting for app..."
  sleep 3
done

echo "Smoke test failed"
exit 1