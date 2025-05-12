.DEFAULT_GOAL := setup
SHELL := bash

VENV := env

ifeq (, $(shell command -v python3 2> /dev/null))
	PY_SYS := python
else
	PY_SYS := python3
endif

ifeq ($(OS),Windows_NT)
	VENV_PY := $(VENV)/Scripts/python.exe
else
	VENV_PY := $(VENV)/bin/python
endif

.PHONY: setup requirements venv

setup: requirements
	$(VENV_PY) setup.py

requirements: venv
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install --upgrade mysql-connector-python

venv:
	@if [ ! -f "$(VENV_PY)" ]; then \
		echo "🔧  Creating virtual environment in $(VENV)"; \
		$(PY_SYS) -m venv $(VENV); \
		$(VENV_PY) -m pip install --upgrade pip; \
		$(VENV_PY) -m pip install -r requirements.txt; \
	else \
		echo "✅  Virtual environment already exists."; \
	fi
