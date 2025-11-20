#!/bin/bash
# Fast ODBC driver detection tests using Docker volume mounts
set -e

echo "========================================================================"
echo "ODBC Driver Detection Tests (Fast Mode)"
echo "========================================================================"
echo ""

# Build base image with ODBC libraries (cached)
echo "Building base image..."
docker build -q -t herbot-test-base - << 'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc unixodbc-dev tdsodbc && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
EOF

# Test 1: Missing pyodbc package
echo ""
echo "Test 1: Missing pyodbc"
echo "----------------------------------------"
docker run --rm -v "$(pwd):/app" -w /app herbot-test-base sh -c \
  "uv pip install --system -e . >/dev/null 2>&1 && \
   python3 -c 'from nhs_herbot.sql import SQLServer; SQLServer(\"s\",\"u\",\"d\")' 2>&1 | tail -2 || true"

# Test 2: Missing system ODBC libraries
echo ""
echo "Test 2: Missing system ODBC libraries"
echo "----------------------------------------"
docker build -q -t test-no-libs - << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
EOF
docker run --rm -v "$(pwd):/app" -w /app test-no-libs sh -c \
  "uv pip install --system -e .[sql] >/dev/null 2>&1 && \
   python3 -c 'from nhs_herbot.sql import SQLServer; SQLServer(\"s\",\"u\",\"d\")' 2>&1 | head -3"

# Test 3: FreeTDS driver
echo ""
echo "Test 3: FreeTDS driver"
echo "----------------------------------------"
docker run --rm -v "$(pwd):/app" -w /app herbot-test-base sh -c \
  "uv pip install --system -e .[sql] >/dev/null 2>&1 && \
   python3 -c 'from nhs_herbot.odbc_utils import validate_odbc_setup; validate_odbc_setup(); print(\"✓ FreeTDS working\")' 2>&1"

# Test 4: Microsoft ODBC driver
echo ""
echo "Test 4: Microsoft ODBC Driver"
echo "----------------------------------------"
if ! docker image inspect test-microsoft-driver &>/dev/null; then
    echo "Building Microsoft driver image (one-time)..."
    docker build -q -t test-microsoft-driver -f tests/driver_tests/Dockerfile.with-microsoft-driver . 2>&1 | tail -1
fi
docker run --rm test-microsoft-driver 2>&1 | grep -v ERROR

echo ""
echo "========================================================================"
echo "Tests completed"
echo "========================================================================"
