#!/bin/bash
# Alembic wrapper script to handle PYTHONPATH and config location

# Set PYTHONPATH to project root
export PYTHONPATH=/mnt/c/data/300.Workspaces/CrewAI-Studio

# Run alembic with correct config file location
alembic -c bend/alembic.ini "$@"
