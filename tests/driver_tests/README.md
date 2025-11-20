# ODBC Driver Detection Tests

Automated validation of ODBC driver detection across different installation scenarios.

## Quick Start

```bash
# Fast tests (~40 seconds)
./tests/driver_tests/run_fast_tests.sh

# Full isolation tests (~2-3 minutes)
./tests/driver_tests/run_docker_tests.sh
```

## Test Scenarios

| Test | Environment | Expected Result |
|------|-------------|-----------------|
| 1 | No pyodbc package | ImportError with pip install command |
| 2 | No system ODBC libraries | DatabaseConnectionError with apt-get/yum commands |
| 3 | FreeTDS driver | Success with warning (recommends Microsoft driver) |
| 4 | Microsoft ODBC Driver | Clean success, no warnings |

## Test Methods

**Fast Tests** - Volume mounts, ~40 seconds
**Full Tests** - Complete isolation, ~2-3 minutes

## Manual Testing

```bash
# Individual scenarios
docker build -t test-scenario-1 -f tests/driver_tests/Dockerfile.no-pyodbc .
docker run --rm test-scenario-1

docker build -t test-scenario-2 -f tests/driver_tests/Dockerfile.no-odbc-libs .
docker run --rm test-scenario-2

docker build -t test-scenario-3 -f tests/driver_tests/Dockerfile.with-odbc .
docker run --rm test-scenario-3

docker build -t test-scenario-4 -f tests/driver_tests/Dockerfile.with-microsoft-driver .
docker run --rm test-scenario-4
```
