#!/bin/bash

# Exit on error
set -e

# Install dependencies
echo "Installing dependencies..."
uv pip install -e ".[dev]"

# Run tests
echo "Running tests..."
pytest tests/integration/test_server.py -v 