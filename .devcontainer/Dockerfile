FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

COPY --from=python:3.13.6-bookworm /usr/local/ /usr/local/

RUN find /etc/apt/sources.list.d -maxdepth 1 -type f -iname '*yarn*' -delete \
    && apt-get update \
    && apt-get install -y --no-install-recommends ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && test "$(command -v rg)" = "/usr/bin/rg"

USER vscode
