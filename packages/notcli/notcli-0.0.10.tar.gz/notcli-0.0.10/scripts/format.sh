#!/bin/bash -e

PACKAGE_PATH="src"

ruff "$PACKAGE_PATH" tests --fix
black "$PACKAGE_PATH" tests