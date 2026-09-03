#!/usr/bin/env bash
set -euo pipefail

python -m pip install --user pipenv
"${HOME}/.local/bin/pipenv" install
