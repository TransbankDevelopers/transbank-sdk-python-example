#!/usr/bin/env bash
set -euo pipefail

sudo chown "$(id -u):$(id -g)" .venv
python -m pip install --user pipenv
"${HOME}/.local/bin/pipenv" install
