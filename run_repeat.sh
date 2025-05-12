#!/bin/bash

# Script to run Chan program files with support for repeat loops using mini_chan.py
# This script chooses the best interpreter for the file based on content

# Check if a file is provided
if [ $# -eq 0 ]; then
  echo "Usage: $0 <filename> [--debug]"
  echo "Example: $0 repeat_demo.chan"
  exit 1
fi

# Check if the file exists
if [ ! -f "$1" ]; then
  echo "Error: File '$1' not found"
  exit 1
fi

# Check for debug flag
DEBUG=""
if [[ "$*" == *"--debug"* ]]; then
  DEBUG="--debug"
fi

# Run the file using mini_chan.py which has the best support for repeat loops
echo "Running $1 with repeat loop support (using mini_chan.py)..."
python3 mini_chan.py "$1" $DEBUG 