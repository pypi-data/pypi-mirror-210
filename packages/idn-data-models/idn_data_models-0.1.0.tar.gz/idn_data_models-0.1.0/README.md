# IDUN Guardian data model library

This library includes the IDUN Guardian data model, which is used by both the frontend and the backend.

## Features

- Data model

Includes mypy types.

## Development environment: devcontainer

This package is developed inside a devcontainer.
To develop, all you have to do is to use VSCode, install the "Remote: Containers" extension, and run the command "Open Folder in Container".
This will start an environment with all tools/dependencies already installed.

### Environment variables

All the environment variables are documented in the [devcontainer docker compose](.devcontainer/docker-compose.yml).

!!! note
    The devcontainer startup script creates 2 dynamic environment variables and writes them to the file `.env`.
    (their names are still visible in docker compose).
    You need to export these variables in the VSCode terminal before running any command like tests:
    `export $(cat .env | xargs)`

### Running tests

VSCode is configured to pick up all env variables (including `.env`) when you run the debugger or when you run tests from the UI.

To run tests in the terminal, see [the command that CI runs](.ci/pre-merge).