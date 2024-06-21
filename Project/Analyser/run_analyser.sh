#!/bin/bash

# Move into the application folder
cd "FastAPI Application"

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found, creating it..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Failed to create the virtual environment"
        exit 1
    fi
fi

# Activate the virtual environment
source .venv/bin/activate

# Check if uvicorn is installed
UVICORN_INSTALLED=$(pip show uvicorn > /dev/null 2>&1; echo $?)
if [ $UVICORN_INSTALLED -ne 0 ]; then
    echo "Uvicorn is not installed in the virtual environment, installing requirements..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements"
        exit 1
    fi
fi

# Move into the src folder
cd "src"

# Run the FastAPI application with uvicorn
uvicorn main:app --workers 4 &
UVICORN_PID=$!
if [ $? -ne 0 ]; then
    echo "Failed to start Uvicorn"
    exit 1
fi

# Wait a few seconds to ensure the server starts
sleep 5

# Open the default URL in the default web browser
xdg-open http://127.0.0.1:8000