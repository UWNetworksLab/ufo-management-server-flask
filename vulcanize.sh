#!/bin/bash

# Script to vulcanize all the Polymer files into one big blob.

# Get the directory where this script is and set ROOT_DIR to that path. This
# allows script to be run from different directories but always act on the
# directory it is within.
ROOT_DIR="$(cd "$(dirname $0)"; pwd)";
STATIC_DIR="${ROOT_DIR}/ufo/static/"

BOWER_OPTIONS="--allow-root --config.interactive=false"

TEMP_FILE_LIST="temp_file_for_vulcanize_list"
HTML_FILE_TO_VULCANIZE="vulcanize_input.html"
VULCANIZED_HTML_FILE="vulcanized.html"

IMPORT_BEFORE_STATEMENT='<link rel="import" href="'
IMPORT_AFTER_STATEMENT='" />'

function runAndAssertCmd ()
{
    echo "Running: $1"
    echo
    # We use set -e to make sure this will fail if the command returns an error
    # code.
    set -e && cd $ROOT_DIR && eval $1
}

function runInStaticDirAndAssertCmd ()
{
  echo "Running: $1"
  # We use set -e to make sure this will fail if the command returns an error
  # code.
  if [ -d  "$STATIC_DIR" ]; then
    echo "In: $STATIC_DIR"
    echo
    set -e && cd $STATIC_DIR && eval $1
  else
    echo "In: $ROOT_DIR"
    echo
    set -e && cd $ROOT_DIR && eval $1
  fi
}

function installVulcanize ()
{
  runAndAssertCmd "sudo npm install -g vulcanize"
}

function updateBowerPackages ()
{
  runAndAssertCmd "bower install $BOWER_OPTIONS"
}

function findHtmlFilesToVulcanize ()
{
  runInStaticDirAndAssertCmd "rm -fr $TEMP_FILE_LIST"
  runInStaticDirAndAssertCmd "rm -fr $HTML_FILE_TO_VULCANIZE"
  runInStaticDirAndAssertCmd "touch $TEMP_FILE_LIST"
  # This searches through the ufo/static/ directory and finds all files that
  # match *html, but excludes index.html, basic.html, files under directories
  # with test in the name, and files under directories with demo in the name.
  # It then sed's the files to remove the prepended ./ and outputs to
  # $TEMP_FILE_LIST.
  runInStaticDirAndAssertCmd "find . -name '*html' -not -name 'index.html' -not -name 'basic.html' -not -path '*test*' -not -path '*demo*' | sed 's|./||' > $TEMP_FILE_LIST"
}

function createSingleHtmlFileToVulcanize ()
{
  runInStaticDirAndAssertCmd "touch $HTML_FILE_TO_VULCANIZE"
  # This reads through $TEMP_FILE_LIST line by line to transform the name of
  # each html file into an import statement by prepending
  # $IMPORT_BEFORE_STATEMENT and appending $IMPORT_AFTER_STATEMENT. This entire
  # set of imports is then output to $HTML_FILE_TO_VULCANIZE.
  # The reason for not doing the prepend and append as part of the sed command
  # above is simply for debugging. Both $TEMP_FILE_LIST and
  # $HTML_FILE_TO_VULCANIZE are removed upon succes, but are kept in case of
  # failure in order to trace what went wrong.
  runInStaticDirAndAssertCmd 'while read line; do echo "${IMPORT_BEFORE_STATEMENT}${line}${IMPORT_AFTER_STATEMENT}"; done < $TEMP_FILE_LIST > $HTML_FILE_TO_VULCANIZE'
  runInStaticDirAndAssertCmd "rm -fr $TEMP_FILE_LIST"
}

function vulcanizeSingleFileForImports ()
{
  runInStaticDirAndAssertCmd "rm -fr $VULCANIZED_HTML_FILE"
  # This finally vulcanizes all the import statements into one flat file,
  # $VULCANIZED_HTML_FILE, with comments removed and scripts inlined.
  runInStaticDirAndAssertCmd "vulcanize $HTML_FILE_TO_VULCANIZE > $VULCANIZED_HTML_FILE --strip-comments --inline-scripts"
  runInStaticDirAndAssertCmd "rm -fr $HTML_FILE_TO_VULCANIZE"
}

function printHelp ()
{
  echo
  echo "Usage: vulcanize.sh [help|--help]"
  echo
  echo "  help, --help   - Prints this help text."
  echo
  echo "If no parameters are specified, this generates a vulcanized html file "
  echo "of bower packages and custom elements which were found under "
  echo "$STATIC_DIR"
  echo
  echo "The output file will be"
  echo "${STATIC_DIR}${VULCANIZED_HTML_FILE}"
  echo
}


if [ "$#" == 0 ] || [ ! "$1" == 'help' && ! "$1" == '--help' ]; then
  installVulcanize
  updateBowerPackages
  findHtmlFilesToVulcanize
  createSingleHtmlFileToVulcanize
  vulcanizeSingleFileForImports
else
  printHelp
  exit 0
fi
