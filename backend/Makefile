.DEFAULT: help
.PHONY: help bootstrap genproto lint makemigrations migrate isort run-api run-dummy test testreport outdated deptree

VENV=.venv
PYTHON=python
PYTEST_PROC_NUM?=4

export SQLALCHEMY_WARN_20=1

help:
	@echo "Please use \`$(MAKE) <target>' where <target> is one of the following:"
	@echo "  help               - show help information"
	@echo "  bootstrap          - setup packaging dependencies and initialize venv"
	@echo "  genproto           - generate protobuf schemas"
	@echo "  lint               - inspect project source code for errors"
	@echo "  makemigrations     - autogenerate database migrations"
	@echo "  migrate            - apply database migrations"
	@echo "  isort              - sort imports according to project conventions"
	@echo "  run-api            - run api service"
	@echo "  run-dummy         - run dummy (micro)service"
	@echo "  test               - run project tests"
	@echo "  testreport         - run project tests and open HTML coverage report"
	@echo "  outdated           - list outdated project requirements"
	@echo "  deptree            - show project dependency tree"

lint:
	$(PYTHON) -m flake8 app tests

makemigrations:
	$(PYTHON) -m app.cli.__main__ alembic revision --autogenerate

migrate:
	$(PYTHON) -m app.cli.__main__ alembic upgrade head

isort:
	$(PYTHON) -m isort app tests

run-api:
	$(PYTHON) -m app.api.__main__

run-dummy:
	$(PYTHON) -m app.dummy.__main__

test:
	$(PYTHON) -m pytest -n $(PYTEST_PROC_NUM)

testreport:
	$(PYTHON) -m pytest -n $(PYTEST_PROC_NUM) --cov-report=html
	xdg-open htmlcov/index.html

outdated:
	$(PYTHON) -m pip list --outdated --format=columns

deptree:
	$(PYTHON) -m pipdeptree
