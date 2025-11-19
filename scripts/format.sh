#!/usr/bin/bash
set -e

ruff check . --fix
ruff format .
