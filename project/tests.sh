#!/bin/bash

if [ ! -d "project" ]; then
  echo "Was not in the project directory. Changing to the project directory."
  cd project
fi

echo "Starting Testing..."

pytest test_pipeline.py --verbose

# Execution:
# Via Git Bash command: sh tests.sh inside the project-directory

# First Testcase takes a "little"