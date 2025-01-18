#!/usr/bin/env bash

# cd into script location
cd "$(dirname "$0")" && \
poetry install --no-root && \
poetry run python main.py

