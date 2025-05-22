.DEFAULT_GOAL := main
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

.PHONY: main setup requirements venv

main: setup
	@echo "🚀 Running main.py…"
	$(VENV_PY) -m  bot

setup: requirements
	@echo "⚙️  Running setup.py…"
	$(VENV_PY) setup.py

requirements: venv
	@echo "📦 Installing/upgrading requirements…"
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
