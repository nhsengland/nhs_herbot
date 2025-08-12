# Using Tox for Multi-Python Version Testing

This repository uses [tox](https://tox.readthedocs.io/) to test the code across multiple Python versions and maintain code quality.

## Available Environments

Run `tox list` to see all available environments:

```bash
tox list
```

### Testing Environments

- **py39**: Run tests with Python 3.9
- **py310**: Run tests with Python 3.10
- **py311**: Run tests with Python 3.11
- **py312**: Run tests with Python 3.12

### Code Quality Environments

- **lint**: Run linting with black, isort, and flake8
- **format**: Format code with black and isort
- **type-check**: Run type checking with mypy

### Documentation Environments

- **docs**: Build documentation with mkdocs
- **docs-serve**: Serve documentation locally

## Common Commands

### Run all default environments
```bash
tox
```

### Run specific environment
```bash
tox run -e py39        # Test with Python 3.9
tox run -e lint        # Run linting
tox run -e format      # Format code
tox run -e type-check  # Type checking
```

### Run multiple environments
```bash
tox run -e py39,py310,lint
```

### Run tests with coverage
The testing environments automatically include coverage reporting. You can see detailed coverage after running any `py*` environment.

### Format code before committing
```bash
tox run -e format
```

### Check code quality
```bash
tox run -e lint
```

## Setting Up Multiple Python Versions

To test across multiple Python versions, you need those Python versions installed on your system.

### Using pyenv (Recommended)
```bash
# Install pyenv first, then:
pyenv install 3.9.18
pyenv install 3.10.13
pyenv install 3.11.7
pyenv install 3.12.1

# Make them available globally
pyenv global 3.12.1 3.11.7 3.10.13 3.9.18
```

### Using deadsnakes PPA (Ubuntu/Debian)
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.9 python3.10 python3.11 python3.12
```

## Configuration

The tox configuration is in `tox.ini`. Key settings:

- **envlist**: Default environments to run
- **isolated_build**: Use PEP 517 isolated builds
- **skip_missing_interpreters**: Continue if some Python versions are missing
- **testenv**: Base configuration for all test environments
- **deps**: Dependencies for each environment

## GitHub Actions Integration

The configuration includes GitHub Actions mapping in the `[gh-actions]` section, which automatically runs the appropriate tox environment based on the Python version in CI.

## Tips

1. **First time setup**: Run `tox run -e format` to format your code
2. **Before committing**: Run `tox run -e lint` to check code quality
3. **Testing changes**: Run `tox run -e py312` for quick feedback (if you have Python 3.12)
4. **Full test suite**: Run `tox` to test everything (requires all Python versions)
5. **Development workflow**: Use `tox run -e format && tox run -e lint && tox run -e py312` for common checks

## Development Dependencies

To install development dependencies including tox:
```bash
pip install -e ".[dev]"
```

This installs all development tools including tox, black, flake8, isort, mypy, and others.
