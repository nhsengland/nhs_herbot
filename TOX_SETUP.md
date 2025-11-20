# Tox Multi-Python Testing Setup

## Quick Start

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -e '.[sql,test]' tox tox-uv

# Run tests
tox                    # All Python versions
tox run -e py312       # Specific version
tox run -e lint        # Code quality
```

## Configuration

- `tox.ini` - Test environments with `tox-uv` for fast installation
- Python 3.9-3.12 supported
- 206 tests, 87% coverage

## Commands

```bash
tox run -e py39,py310,py311,py312  # All versions
tox run -e lint                    # Black, isort, flake8
tox run -e format                  # Auto-format
tox run -e type-check              # Mypy
tox run -e docs                    # Build docs
```
