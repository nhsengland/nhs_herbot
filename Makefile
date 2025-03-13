#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = nhs_herbot
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
.PHONY: requirements
requirements: 
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Install Python Dependencies Quietly
.PHONY: requirements_quiet
requirements_quiet: 
	$(PYTHON_INTERPRETER) -m pip install -q -U pip
	$(PYTHON_INTERPRETER) -m pip install -q -r requirements.txt


## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

## Alias for clean
.PHONY: clear
clear: clean

## Delete the current python environment. Nuke it from orbit.
.PHONY: nuke
nuke: clean
	find . -type d -name "*.venv" -exec rm -rf {} +

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	$(PYTHON_INTERPRETER) -m flake8 $(PROJECT_NAME)
	$(PYTHON_INTERPRETER) -m isort --check --diff --profile black $(PROJECT_NAME)
	$(PYTHON_INTERPRETER) -m black --check --config pyproject.toml $(PROJECT_NAME)

## Format source code with black
.PHONY: format
format:
	$(PYTHON_INTERPRETER) -m isort --profile black $(PROJECT_NAME)
	$(PYTHON_INTERPRETER) -m black --config pyproject.toml $(PROJECT_NAME)

## Set up python interpreter environment
.PHONY: create_environment
create_environment:
	$(PYTHON_INTERPRETER) -m venv .venv


## Set up pre-commits and run them on all files
.PHONY: pre-commits
pre-commits: requirements_quiet
	$(PYTHON_INTERPRETER) -m pre_commit autoupdate
	$(PYTHON_INTERPRETER) -m pre_commit install
	$(PYTHON_INTERPRETER) -m pre_commit run --all-files

.PHONY: create_branch
branch:
	@read -p "Enter your name: " name; \
	read -p "Enter JIRA ticket number: " ticket; \
	read -p "Enter branch description: " desc; \
	if [ -z "$$ticket" ]; then \
		git checkout -b $$(echo "$$name/$$desc" | tr ' ' '-'); \
	else \
		git checkout -b $$(echo "$$name/$$ticket-$$desc" | tr ' ' '-'); \
	fi


## Create test files for all python files in the project
.PHONY: create_tests
create_tests:
	@find $(PROJECT_NAME) -type f -name "*.py" | while read file; do \
		if [ $$(basename $$file) != "__init__.py" ]; then \
			new_path=tests/unittests/$$(echo $$file | sed 's|^[^/]*/||' | awk -F/ '{for(i=1;i<=NF;i++)$$i="test_"$$i; print}' OFS=/); \
			mkdir -p $$(dirname $$new_path); \
			if [ ! -f $$new_path ]; then \
				touch $$new_path; \
				echo "\"\"\"\nTests for $$(echo $$file | sed 's|/|.|g' | sed 's|\.py||')\n\"\"\"\nimport pytest\n" >> $$new_path; \
				echo "import $$(echo $$file | sed 's|/|.|g' | sed 's|\.py||')" >> $$new_path; \
				echo "\n\nclass TestExample:" >> $$new_path; \
				echo "    \"\"\"Example test class\"\"\"" >> $$new_path; \
				echo "    def test_example(self):" >> $$new_path; \
				echo "        \"\"\"Example test case\"\"\"" >> $$new_path; \
				echo "        assert True" >> $$new_path; \
			fi \
		fi \
	done

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

## Run Pipeline
.PHONY: run
run: requirements_quiet
	$(PYTHON_INTERPRETER) $(PROJECT_NAME)/pipeline.py

## Run all tests
.PHONY: test
test: requirements_quiet
	$(PYTHON_INTERPRETER) -m pytest

## Run only unittests
.PHONY: unittest
unittest: requirements_quiet
	$(PYTHON_INTERPRETER) -m pytest tests/unittests 

## Run only end-to-end (e2e) tests
.PHONY: e2e
e2e: requirements_quiet
	$(PYTHON_INTERPRETER) -m pytest tests/e2e_tests

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

## Show some helpful information!

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z0-9_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
