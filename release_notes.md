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

#### **Technical Details**

- **Dependencies**: Added support for `pyodbc` for SQL Server connectivity
- **Code Quality**: Maintained comprehensive test coverage with new test suite for database functionality
- **Compatibility**: Continues to support Python 3.9-3.12

#### **Core Functionality**

This release maintains all existing features while adding database capabilities:

- CSV data loading with custom error handling
- Column name normalization and data processing
- Dataset joining with validation
- Financial date utilities and conversions
- **NEW**: SQL Server database operations
- Comprehensive logging and error handling

#### **For NHS England Users**

This release strengthens HERBOT's capability as a comprehensive toolkit for healthcare data analysis, particularly for teams working with both file-based and database-stored healthcare datasets in Reproducible Analytical Pipelines (RAPs).

#### **Installation**

```bash
pip install nhs-herbot==2025.08.08
```

---

*This release represents continued commitment to providing NHS England data analysts and researchers with reliable, standardized tools for healthcare data processing.*
