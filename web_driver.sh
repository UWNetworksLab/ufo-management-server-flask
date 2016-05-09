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
  echo "Running: python ui_test_suite.py with hidden params"
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
  return $?
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

# These tests run from the local machine pointing out to whatever instance is
# passed as the server url.
function runUITestsLocally ()
{
  runInTestDirAndAssertCmd "python ui_test_suite.py --server_url='$SERVER_URL' --username='$USERNAME' --password='$PASSWORD'"
}

# These tests run on Travis but tunneling to a Sauce Labs machine. They will
# still point to whatever instance is passed as the server url.
function runUITestsOnSauceLabs ()
{
  # The if statement below is to ensure that remote tests only run against the
  # production branch. Travis sets TRAVIS_BRANCH to the target of a pull
  # request for those types of builds. For regular commits and pushes,
  # TRAVIS_BRANCH is branch being built , so if you're pushing from master to
  # production, TRAVIS_BRANCH would say master (unless its a pull request).
  # We check that TRAVIS_BRANCH is in fact production and that the override is
  # set to auto (the typical case). If the override is set to true, then we
  # ignore TRAVIS_BRANCH and run anyway. This should only happen when we need
  # to reexecute web driver tests if the first run failed. However, this should
  # not be done often as running multiple tests at the same time will cause
  # interference (since both modify a standing instance).
  if [ [ "$TRAVIS_BRANCH" == 'production' ]  &&  [ "$TRAVIS_WEB_DRIVER_OVERRIDE" == 'auto' ] ] || [ "$TRAVIS_WEB_DRIVER_OVERRIDE" == 'true' ]; then
    runInTestDirAndAssertCmd "python ui_test_suite.py --server_url='$SERVER_URL' --username='$TRAVIS_ADMIN_USERNAME' --password='$TRAVIS_ADMIN_PASSWORD' --sauce-username='$SAUCE_USERNAME' --sauce-access-key='$SAUCE_ACCESS_KEY' --travis-job-number='$TRAVIS_JOB_NUMBER'"
  else
    exit 0
  fi
}

function printHelp ()
{
  echo
  echo "Usage: web_driver.sh [install|test]"
  echo
  echo "  install   - Installs web driver from chromedriver on googleapis."
  echo "  test      - Runs the UI test suite."
  echo
  echo "If you have trouble with permissions while installing, try using sudo."
  echo "Example: sudo ./web_driver.sh install"
  echo
  echo "The test command takes three additional arguments as follows:"
  echo "test server_url username password"
  echo "Example:"
  echo "./web_driver.sh test https://my-server-staging.appspot.com"
  echo "ui_tester@mydomain.com your-password-goes-here"
  echo
  echo "The test command can also be run against remote servers, but relies on"
  echo "environment variables to do so. This is NOT advised as it will require"
  echo "Sauce Labs account and connecting through Travis CI. If you think this"
  echo "is what you need, then setup the following environment variables:"
  echo "TRAVIS_ADMIN_USERNAME is the admin username for the nightly instance."
  echo "TRAVIS_ADMIN_PASSWORD is the admin password for the nightly instance."
  echo "SAUCE_USERNAME is the username to an account on Sauce Labs."
  echo "SAUCE_ACCESS_KEY is the access key to run an account on Sauce Labs."
  echo "TRAVIS_JOB_NUMBER is the current job number for the running process to"
  echo "denote one from another (for simultaneous sauce labs tunnels)."
  echo
}


if [ "$1" == 'install' ]; then
  installChromeDriver
elif [ "$1" == 'test' ]; then
  if [ $# -eq 4 ]; then
    SERVER_URL=$2
    USERNAME=$3
    PASSWORD=$4
    runUITestsLocally
  elif [ -z "$TRAVIS_ADMIN_USERNAME" ]  ||  [ -z "$TRAVIS_ADMIN_PASSWORD" ]  ||  [ -z "$SAUCE_USERNAME" ]  ||  [ -z "$SAUCE_ACCESS_KEY" ]  ||  [ -z "$TRAVIS_JOB_NUMBER" ]; then
    # The if statement above just checks that all the necessary values are
    # present for doing remote UI tests. If they aren't, then we just fail out
    # here.
    printHelp
    exit 0
  else
    SERVER_URL="http://ufo-nightly.herokuapp.com"
    runUITestsOnSauceLabs
  fi
else
  printHelp
  exit 0
fi
