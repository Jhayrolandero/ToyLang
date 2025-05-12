#!/bin/bash

# Script to run Chan program files with support for repeat loops

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

# Run the file using the repeat_feature.py script
python3 repeat_feature.py $1 $DEBUG 