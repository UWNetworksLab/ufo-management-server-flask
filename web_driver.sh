#!/bin/bash

# Script to install the chrome web driver locally to run web driver
# functional tests.

# Get the directory where this script is and set ROOT_DIR to that path. This
# allows script to be run from different directories but always act on the
# directory it is within.
ROOT_DIR="$(cd "$(dirname $0)"; pwd)";

CHROME_DRIVER_VERSION="2.20"
CHROME_DRIVER_FILE="chromedriver_linux64.zip"
CHROME_DRIVER_LOCATION="http://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/${CHROME_DRIVER_FILE}"
CHROME_DRIVER_DIR="chrome_driver"
TEST_DIR="${ROOT_DIR}/tests/ui/"

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

function runInTestDirAndAssertCmd ()
{
  echo "Running: $1"
  # We use set -e to make sure this will fail if the command returns an error
  # code.
  if [ -d  "$TEST_DIR" ]; then
    echo "In: $TEST_DIR"
    echo
    set -e && cd $TEST_DIR && eval $1
  else
    echo "In: $ROOT_DIR"
    echo
    set -e && cd $ROOT_DIR && eval $1
  fi
}

function installChromeDriver ()
{
  runAndAssertCmd "pip install -r requirements.txt"
  runAndAssertCmd "wget $CHROME_DRIVER_LOCATION"
  runAndAssertCmd "unzip $CHROME_DRIVER_FILE"
  runAndAssertCmd "rm $CHROME_DRIVER_FILE"
  runAndAssertCmd "chmod +x chromedriver"
  runAndAssertCmd "mkdir $CHROME_DRIVER_DIR"
  runAndAssertCmd "mv chromedriver ${CHROME_DRIVER_DIR}/"
}

function runUITests ()
{
  runInTestDirAndAssertCmd "python ui_test_suite.py --server_url='$SERVER_URL' --email='$EMAIL' --password='$PASSWORD'"
}

function printHelp ()
{
  echo
  echo "Usage: web_driver.sh [install|test]"
  echo
  echo "  install   - Installs web driver from chromedriver on googleapis."
  echo "  test      - Runs the UI test suite."
  echo
  echo "The test command takes three additional arguments as follows:"
  echo "test server_url email password"
  echo "Example:"
  echo "./web_driver.sh test https://my-server-staging.appspot.com"
  echo "ui_tester@mydomain.com your-password-goes-here"
  echo
  echo "If you have trouble with permissions while installing, try using sudo."
  echo "Example: sudo ./web_driver.sh install"
  echo
}


if [ "$1" == 'install' ]; then
  installChromeDriver
elif [ "$1" == 'test' ] && [ $# -eq 4 ]; then
  SERVER_URL=$2
  EMAIL=$3
  PASSWORD=$4
  runUITests
else
  printHelp
  exit 0
fi