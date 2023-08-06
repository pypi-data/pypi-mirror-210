#!/bin/bash -e

PACKAGE_PATH="src"

ruff "$PACKAGE_PATH"
black "$PACKAGE_PATH" --check
