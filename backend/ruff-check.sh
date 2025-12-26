#!/bin/bash
# Script to ensure ruff uses the same config as pre-commit
# Run this before committing to ensure consistency

cd "$(dirname "$0")"
poetry run ruff check --fix .
poetry run ruff format .
