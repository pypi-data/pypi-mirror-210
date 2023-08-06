#!/bin/bash -e

coverage run -m pytest -v
coverage report -m --skip-covered
exit 0
