#!/bin/bash

echo "========================================"
echo "Plex Poster Set Helper - Setup Script"
echo "========================================"
echo ""

python3 setup.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Setup failed! Please check the error messages above."
    exit 1
fi

echo ""
echo "Setup complete! You can now run the application."
