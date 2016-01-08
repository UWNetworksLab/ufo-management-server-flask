#!/bin/bash

# Get the directory where this script is and set ROOT_DIR to that path. This
# allows script to be run from different directories but always act on the
# directory it is within.
ROOT_DIR="$(cd "$(dirname $0)"; pwd)";


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

function testOnTravis ()
{
  runAndAssertCmd "pip install virtualenv"
  runAndAssertCmd "virtualenv venv"
  runAndAssertCmd ". venv/bin/activate"
  runAndAssertCmd "pip install -r requirements.txt"
  runAndAssertCmd "python setup_database.py"
  runAndAssertCmd "npm install"
}

testOnTravis
