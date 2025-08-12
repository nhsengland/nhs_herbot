# NHS HERBOT

[![CCDS: Project Template](https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter)](https://cookiecutter-data-science.drivendata.org/ "cookiecutter-data-science")
[![RAP Status: Work in Progress](https://img.shields.io/badge/RAP_Status-WIP-red)](https://nhsdigital.github.io/rap-community-of-practice/introduction_to_RAP/levels_of_RAP/ "WIP RAP")
[![licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](https://opensource.org/licenses/MIT "MIT License")
[![licence: OGL3](https://img.shields.io/badge/Licence-OGL3-darkgrey "licence: Open Government Licence 3")](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
[![JIRA EPIC: DC-908](https://img.shields.io/badge/JIRA-DC--908-purple?link=https%3A%2F%2Fnhsd-jira.digital.nhs.uk%2Fbrowse%2FDC-908)](https://nhsd-jira.digital.nhs.uk/browse/DC-908 "DC-908")
[![Tests and Linting](https://github.com/nhsengland/nhs_herbot/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/nhsengland/nhs_herbot/actions/workflows/python-package.yml)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-blue)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/downloads/release/python-3110/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/downloads/release/python-3120/)

``` ascii
.....................................................................
...................####--+++####.....................................
...................#############.....................................
...................#####++++####.....................................
....................-##+---+###-.....................................
.....................##+---+-###+....................................
.....................##-+---+-###....................................
....................+##++----#+###...................................
....................###+-----+#####..................................
....................##-+------######.................................
...................+##-+------+#-###.................................
...................###-+-------##-###................................
...................##++--------+######...............................
...................##++---------##+####..............................
..................+##-+---------+##+####.............................
..................###------------###-####............................
..................##+-------------##+-####...........................
.................+##--++----------+###-###+..........................
.................###---+##+-----+####++-####.........................
.................##+-+++--++########+--++###+........................
...............+###+-++---+#####+-+++-+-+-##########.................
...........+#######+---+##+-------+####++--###########...............
........+#########-+---####++-----##+###-++--#+-+-#####..............
.......+#####++##-#----####+------####+###--++#++-+####..............
.......###+-+-++-++--+-+##++#########+++###+++##+######..............
.......#####--+#-++-+##+###++++#######++++##+#+#######+..............
.......+########++#++######+++++--#######-+++#-#####+................
........-########-+##+++#-##+++++########+++#####+###############+...
..............####-+########++-+############++######################.
..............+#####+--+###+--+++---+-+-++--########+##+###+++#++###.
.........+##############+-++-----------+#####+####-###############+#.
......#############-+-+##################+#+-################-+--++#.
....+#####++######+-+++---++-+--+++-++--++---+++-+###########++---+#.
.-#####+--+#+++##+------++##########-+#+-+++###########....###----+#.
.#####----+######+---+++++##-++++++#####+##########-###+..+###++++##.
.##+-------+##+--+++#################++##+#-----+###+###..###+++--#+.
.#---++++++#########################-+++#+#--+-+++++-###..######+#-#.
.###############+++++++++###+-#++----++++-++++++++#+++##.-##+++++++#.
.################-+###++++####+-######+++++#+++--+++-###-+##########.
.-+#######+-...+##+#####################+---------+#+-###-##########.
................-##+++####++++++-------------------+#####-.+#######+.
.................###+--------------------------------+-###...........
.................###-++++--------------------+###+---++###...........
.................-##-------------++#############+++--+####...........
..................##++++########################+++---+###...........
..................########+############+++######+++----###...........
..................-############++##......####################........
........................#######++##......####################........
........................##---++++##......####################........
........................##----+--##......####################........
........................##+--++-+##......##--------------##..........
......................+###-+++++-######..##--------------####-.......
....................###################+.##--------------+#####-.....
....................#####+########+-+###.##+----------------+###.....
....................####++--+###########.+#+--------++++------##+....
....................+##################-.+#+--------++++++++---##....
.....................+##########+----+#-.##+----++++++++++++++-##....
......................##--------------##.-##-++++------------+##-....
......................+##-------------##..#####++++++++++++++##+.....
.......................+#+------------##..+##++++++++++++++##+.......
........................##++----------+#+............................
......................+###++-----------##+...........................
.....................-###-+-------------##...........................
.....................+#+#+++------------##...........................
.....................+#-+--------------+#-...........................
.....................+#+-++----++++-++###............................
.....................................................................
```

*Hi there, I am HERBOT (pronounced Herbert)! Healthcare's Handy, Easy, and Reusable Box of Tricks!*

## Project Description

NHS HERBOT (Healthcare's Handy, Easy, and Reusable Box of Tricks) is a Python package providing common utilities and functions for healthcare data analysis and processing. This toolkit is designed for NHS England data analysts, researchers, and developers working with healthcare datasets in Reproducible Analytical Pipelines (RAPs).

**Intended Purpose:** To standardise and simplify common data processing tasks across NHS England analytical projects, reducing code duplication and ensuring consistent data handling practices.

**Operating Environment:** Python-based data analysis environments, suitable for use in NHS England's analytical infrastructure and local development environments.

**Intended Users:** Data analysts, data scientists, and developers within NHS England working on healthcare data analysis projects.

## Development Status

**Current Status:** Work in Progress (Alpha)  
**Version:** 2025.04.02  
**Maintenance:** Actively maintained  
**Last Updated:** August 2025

## Contact Information

**Primary Maintainer:** [Joseph Wilson](https://github.com/josephwilson8-nhs)  
**Contact:** [Contact via GitHub Issues](https://github.com/nhsengland/nhs_herbot/issues) for project-related queries

## Data Description

This project processes and produces various types of healthcare data:

**Data Dependencies:**

- CSV files containing healthcare datasets
- SQL Server databases with healthcare information
- Date/time data in various formats including financial year periods

**Data Outputs:**

- Processed pandas DataFrames
- Normalised data with standardised column names
- Joined datasets from multiple sources
- Date/time conversions for financial year reporting

## Prerequisites and Dependencies

**Programming Requirements:**

- Python 3.9 or higher
- pandas (data manipulation)
- loguru (logging)
- numpy (numerical operations)
- tqdm (progress bars)

**Optional Dependencies:**

- SQL Server connectivity drivers (for database operations)
- pytest (for running tests)
- black, flake8, isort (for development and code quality)

**System Requirements:**

- Compatible with Windows, macOS, and Linux
- Sufficient memory to handle your datasets in pandas DataFrames

## Installation and Usage

### Installation

Install NHS HERBOT using pip:

```bash
pip install nhs-herbot
```

Or for development:

```bash
git clone https://github.com/nhsengland/nhs_herbot.git
cd nhs_herbot
pip install -e .
```

### Basic Usage

```python
import nhs_herbot as herbot

# Load and process CSV data
data = herbot.load_csv('your_data.csv')

# Normalise column names
normalised_data = herbot.normalise_column_names(data)

# Connect to SQL Server and query data
with herbot.SQLServer(server='your_server', database='your_db') as sql:
    # Read data
    results = sql.query('SELECT * FROM your_table')
    
    # Write data
    sql.write_dataframe(data, 'new_table', if_exists='replace')
    
    # Execute non-query operations
    rows_affected = sql.execute_non_query('UPDATE table SET status = ?', {'status': 'processed'})
    
    # Bulk insert for large datasets
    sql.bulk_insert(large_df, 'bulk_table', batch_size=5000)
    
    # Check if table exists
    if sql.table_exists('target_table'):
        print("Table exists!")

# Join datasets
joined_data = herbot.join_datasets(left_df, right_df, join_columns=['id'])

# Convert financial dates
date_data = herbot.convert_fin_dates(fin_month=4, fin_year=2024)
```

### Core Functionality

- **Data Loading:** CSV file loading with custom error handling
- **Data Processing:** Column name normalisation and data type conversion
- **Database Operations:** SQL Server connectivity, querying, and data writing
  - Read operations: Execute SELECT queries and load results into DataFrames
  - Write operations: Insert DataFrames, execute non-queries, bulk operations
  - Table management: Create tables, check existence, transaction support
- **Data Joining:** Flexible dataset joining with validation
- **Date Utilities:** Financial year date conversions and parsing
- **Error Handling:** Custom exceptions for robust data pipelines

### Running Tests

```bash
pytest tests/
```

## Licence

This project is dual-licensed under:

- **MIT License** - See [LICENSE](LICENSE) file for software components
- **Open Government Licence v3.0** - For documentation and non-software content

## Legal and Regulatory Requirements

This software is developed for use within NHS England and follows:

- NHS England's open source policy and guidelines
- Data protection requirements as per UK GDPR
- NHS Information Governance standards
- Government Digital Service (GDS) coding standards

**Important:** Users must ensure compliance with local data governance policies when using this toolkit with healthcare data. This software does not include any patient data or identifiable information.
