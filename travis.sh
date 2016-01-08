#!/bin/bash

# Get the directory where this script is and set ROOT_DIR to that path. This
# allows script to be run from different directories but always act on the
# directory it is within.
ROOT_DIR="$(cd "$(dirname $0)"; pwd)";
UP_DIR="$(cd ..; pwd)";


# A simple bash script to run commands to setup and install all dev
# dependencies (including non-npm ones)
function runAndAssertCmd ()
{
    echo "Running: $1"
    echo
    # We use set -e to make sure this will fail if the command returns an error
    # code.
    set -e && cd $ROOT_DIR && eval $1
}

function runInUfOAndAssertCmd ()
{
  echo "Running: $1"
  # We use set -e to make sure this will fail if the command returns an error
  # code.
  if [ -d  "$UFO_MS_LOCAL_OTHER_LIB" ]; then
    echo "In: $UFO_MS_LOCAL_OTHER_LIB"
    echo
    set -e && cd $UFO_MS_LOCAL_OTHER_LIB && eval $1
  else
    echo "In: $UFO_MS_LOCAL_DIR"
    echo
    set -e && cd $UFO_MS_LOCAL_DIR && eval $1
  fi
}

function testOntravis ()
{
  runAndAssertCmd "pip install virtualenv"
  runAndAssertCmd "virtualenv venv"
  runAndAssertCmd ". venv/bin/activate"
  runAndAssertCmd "pip install -r requirements.txt"
  runAndAssertCmd "python setup_database.py"
  runAndAssertCmd "npm install"
}

testOntravis
