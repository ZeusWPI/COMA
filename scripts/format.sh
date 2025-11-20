#!/usr/bin/env bash
set -e

ruff check app --fix
ruff format app
