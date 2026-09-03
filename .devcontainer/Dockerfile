FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

COPY --from=python:3.13.6-bookworm /usr/local/bin/python3.13 /usr/local/bin/python3.13
COPY --from=python:3.13.6-bookworm /usr/local/bin/python3.13-config /usr/local/bin/python3.13-config
COPY --from=python:3.13.6-bookworm /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=python:3.13.6-bookworm /usr/local/lib/libpython3.13.so.1.0 /usr/local/lib/libpython3.13.so.1.0

RUN find /etc/apt/sources.list.d -maxdepth 1 -type f -iname '*yarn*' -delete \
    && apt-get update \
    && apt-get install -y --no-install-recommends ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && ldconfig \
    && test "$(command -v rg)" = "/usr/bin/rg" \
    && ln -sf /usr/local/bin/python3.13 /usr/local/bin/python3 \
    && ln -sf /usr/local/bin/python3.13 /usr/local/bin/python

USER vscode
