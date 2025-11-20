# ODBC Setup for SQL Server

## Installation

```bash
# Install package with SQL support
uv pip install nhs-herbot[sql]

# System libraries (Ubuntu/Debian)
sudo apt-get install unixodbc unixodbc-dev

# SQL Server driver (choose one)
sudo apt-get install tdsodbc  # FreeTDS (open source)
# OR Microsoft driver: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server
```

## How It Works

Automatic detection checks:

1. `pyodbc` package installed
2. System ODBC libraries present
3. ODBC drivers registered

Clear error messages guide you to fix missing components.

## Troubleshooting

| Error | Solution |
|-------|----------|
| `libodbc.so.2: cannot open shared object file` | `sudo apt-get install unixodbc unixodbc-dev` |
| `No ODBC drivers registered` | Install `tdsodbc` or Microsoft driver |
| Connection fails | Check drivers: `odbcinst -q -d` |

## Testing

```bash
./tests/driver_tests/run_fast_tests.sh  # ~27s validation
```
