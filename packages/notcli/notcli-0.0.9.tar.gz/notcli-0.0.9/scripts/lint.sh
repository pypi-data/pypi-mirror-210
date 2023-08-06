#!/bin/bash -e

PACKAGE_PATH="src"

ruff "$PACKAGE_PATH" tests
black "$PACKAGE_PATH" tests --check
