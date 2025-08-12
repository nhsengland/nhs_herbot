### NHS HERBOT v2025.08.12

*Healthcare's Handy, Easy, and Reusable Box of Tricks - Major Developer Experience Upgrade!*

#### **🚀 Major New Features**

- **Multi-Python Version Testing Infrastructure**: Complete tox-based testing setup
    - Support for Python 3.9, 3.10, 3.11, and 3.12
    - Automated testing across all supported Python versions
    - Comprehensive lint, format, and type-check environments
    - GitHub Actions integration with automatic version mapping

- **Professional Development Environment**: Enhanced developer experience
    - Standardized code formatting with black and isort
    - Type checking with mypy (lenient configuration for existing codebase)
    - Flake8 linting for code quality assurance
    - Optional development dependencies via `pip install -e .[dev]`

#### **🔧 Enhancements**

- **Python 3.9 Compatibility**: Full backward compatibility improvements
    - Fixed Union type syntax for Python 3.9 compatibility
    - Consistent import ordering across all modules
    - Verified test suite passes on all supported Python versions

- **Project Configuration**: Enhanced pyproject.toml with professional setup
    - Added Python 3.9-3.12 classifiers for proper package metadata
    - Defined optional dependencies for test, dev, and docs workflows
    - Comprehensive tool configurations for development tools

- **GitHub Actions CI/CD**: Modernized continuous integration
    - Replaced manual setup with tox-based testing workflow
    - Separate jobs for testing and quality assurance
    - Matrix strategy for testing across Python versions

- **Testing Improvements**: Better test practices
    - Migrated from tempfile to pytest's tmp_path fixture
    - Cleaner, more maintainable test code
    - Enhanced test reliability and consistency

#### **📊 Technical Metrics**

- **Test Coverage**: Maintains 90% code coverage with 202 passing tests
- **Code Quality**: Zero linting issues, all type checks pass
- **Performance**: Optimized development workflow with ~7-10 second full test runs
- **Compatibility**: Verified working across Python 3.9-3.12

#### **🛠 Development Infrastructure**

- **Multi-Environment Testing**:

```bash
tox                    # Run all environments
tox -e py39,py312     # Test specific versions
tox -e lint           # Code quality checks
tox -e format         # Auto-format code
tox -e type-check     # Type checking
```

- **Enhanced Documentation**: Comprehensive setup guides
    - Detailed tox usage instructions
    - Developer workflow documentation
    - GitHub Actions integration guide

#### **Core Functionality**

All existing features remain fully functional with enhanced reliability:

- CSV data loading with custom error handling
- Column name normalization and data processing
- Dataset joining with validation
- Financial date utilities and conversions
- SQL Server database operations
- Comprehensive logging and error handling

#### **For NHS England Developers**

This release transforms HERBOT into an enterprise-grade development platform:

- **Consistent Development Environment**: All team members use the same tools and standards
- **Automated Quality Assurance**: Pre-commit hooks and CI/CD prevent quality issues
- **Multi-Python Support**: Teams can confidently use different Python versions
- **Professional Workflow**: Modern development practices for RAP projects

#### **Breaking Changes**

None - this release is fully backward compatible.

#### **Installation**

```bash
# Standard installation
pip install nhs-herbot==2025.08.12

# Development installation with all tools
pip install -e .[dev]
```

#### **Upgrade Path**

From any previous version:

```bash
pip install --upgrade nhs-herbot==2025.08.12
```

---

*This release represents a significant investment in developer experience and code quality, establishing HERBOT as a professional-grade toolkit for NHS England's analytical infrastructure.*

### NHS HERBOT v2025.08.08

*Healthcare's Handy, Easy, and Reusable Box of Tricks continues to evolve!*

#### **New Features**

- **Database Connectivity**: Added new `SQLServer` class for robust SQL Server database interactions
    - Support for Active Directory Interactive authentication
    - Context manager support for automatic connection cleanup
    - Query execution from both strings and SQL files with parameter substitution
    - Comprehensive error handling with custom exceptions
    - Connection timeout configuration

#### **Enhancements**

- **Documentation Improvements**: Extensively updated README.md with:
    - Clearer project descriptions and intended use cases
    - Enhanced installation and usage instructions
    - Comprehensive code examples for all core functionality
    - Better structured development status and contact information
    - Improved guidance on data governance and compliance

- **Error Handling**: Enhanced custom exception framework with new database-specific exceptions:
    - `DatabaseConnectionError` for connection failures
    - `SQLExecutionError` for query execution issues
    - `InvalidSQLParametersError` for parameter validation

#### **Technical Details v2025.08.08**

- **Dependencies**: Added support for `pyodbc` for SQL Server connectivity
- **Code Quality**: Maintained comprehensive test coverage with new test suite for database functionality
- **Compatibility**: Continues to support Python 3.9-3.12

#### **Core Functionality v2025.08.08**

This release maintains all existing features while adding database capabilities:

- CSV data loading with custom error handling
- Column name normalization and data processing
- Dataset joining with validation
- Financial date utilities and conversions
- **NEW**: SQL Server database operations
- Comprehensive logging and error handling

#### **For NHS England Users v2025.08.08**

This release strengthens HERBOT's capability as a comprehensive toolkit for healthcare data analysis, particularly for teams working with both file-based and database-stored healthcare datasets in Reproducible Analytical Pipelines (RAPs).

#### **Installation v2025.08.08**

```bash
pip install nhs-herbot==2025.08.08
```

---

*This release represents continued commitment to providing NHS England data analysts and researchers with reliable, standardized tools for healthcare data processing.*
