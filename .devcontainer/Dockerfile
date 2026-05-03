FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Remove the broken Yarn repository to prevent apt-get update from failing
RUN rm -f /etc/apt/sources.list.d/yarn.list