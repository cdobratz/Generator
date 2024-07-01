#!/bin/bash

# Run the Python script
python src/main.py

# Change to the public directory
cd src/public

# Start the web server
python -m http.server 8888