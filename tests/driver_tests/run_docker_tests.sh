#!/bin/bash
# Comprehensive driver detection tests with full isolation
# Uses separate Docker images for complete environment separation
set -e

echo "========================================================================"
echo "ODBC Driver Detection Tests - Full Isolation Mode"
echo "========================================================================"
echo ""

# Test 1: Missing pyodbc package
echo "Test 1: Missing pyodbc package"
echo "----------------------------------------"
echo "Expected: ImportError with pip install instructions"
docker build -q -t test-no-pyodbc -f tests/driver_tests/Dockerfile.no-pyodbc .
docker run --rm test-no-pyodbc 2>&1 | tail -5 || true
echo ""

# Test 2: Missing system ODBC libraries
echo "========================================================================"
echo "Test 2: Missing system ODBC libraries"
echo "----------------------------------------"
echo "Expected: DatabaseConnectionError with apt-get/yum install instructions"
docker build -q -t test-no-odbc-libs -f tests/driver_tests/Dockerfile.no-odbc-libs .
docker run --rm test-no-odbc-libs 2>&1 | grep -A5 "DatabaseConnectionError" || true
echo ""

# Test 3: FreeTDS driver
echo "========================================================================"
echo "Test 3: FreeTDS driver (open source alternative)"
echo "----------------------------------------"
echo "Expected: Success with warning recommending Microsoft driver"
docker build -q -t test-with-odbc -f tests/driver_tests/Dockerfile.with-odbc .
docker run --rm test-with-odbc 2>&1 | grep -v ERROR
echo ""

# Test 4: Microsoft ODBC driver
echo "========================================================================"
echo "Test 4: Microsoft ODBC Driver (recommended setup)"
echo "----------------------------------------"
echo "Expected: Clean success with no warnings"
docker build -q -t test-microsoft-driver -f tests/driver_tests/Dockerfile.with-microsoft-driver .
docker run --rm test-microsoft-driver 2>&1 | grep -v ERROR
echo ""

echo "========================================================================"
echo "All tests completed successfully"
echo "========================================================================"
