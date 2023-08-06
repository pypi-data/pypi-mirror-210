#!/bin/bash -e

PACKAGE_PATH="src"

ruff "$PACKAGE_PATH" --fix
black "$PACKAGE_PATH"