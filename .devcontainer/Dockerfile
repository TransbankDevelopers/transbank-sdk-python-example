FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

# Keep project runtime aligned with Pipfile's exact Python requirement.
COPY --from=python:3.13.6-bookworm /usr/local/ /usr/local/

# The base image may contain a stale Yarn repository whose signing key is unavailable.
RUN find /etc/apt/sources.list.d -maxdepth 1 -type f -iname '*yarn*' -delete \
    && apt-get update \
    && apt-get install -y --no-install-recommends ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && test "$(command -v rg)" = "/usr/bin/rg"

USER vscode
