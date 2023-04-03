#!/bin/bash

# Activate the virtual environment
source .venv/Scripts/activate

# Change directory to the directory where your main file resides
cd ToDo

# Start the FastAPI server
uvicorn main:app --reload
