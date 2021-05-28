#!/bin/sh
# Shell script to test the i18ndude command in tox.
# In tox commands you cannot use shell constructs like double pipes.
# So this command as it was in .travis.yml will not work:
# bin/i18ndude find-untranslated src/i18ndude/tests || echo 'find-untranslated is expected to give errors for missing translations'
# I work around this by creating a shell script that tox copies to the tox envs.
#
# This script expects to be called with the path to the i18ndude script.
# It takes the directory of the test script itself and looks for test files there.
I18NDUDE=$1
TESTDATA_DIR="$(dirname $(realpath $0))/../testdata"
INPUT_DIR="$TESTDATA_DIR/input"

# First we call it with one file in there for which it should not find problems.
GOOD_FILE="$INPUT_DIR/test1.pt"
if ! $I18NDUDE find-untranslated $GOOD_FILE > /dev/null; then
    echo "ERROR: find-untranslated unexpectedly reported errors for missing translations in $GOOD_FILE"
    exit 1
fi
echo "GOOD: find-untranslated did not report errors for missing translations in $GOOD_FILE"

# Now try a command where find-untranslated should report errors:
if $I18NDUDE find-untranslated $INPUT_DIR > /dev/null; then
    echo "ERROR: find-untranslated is expected to report errors for missing translations in $INPUT_DIR"
    exit 1
fi
echo "GOOD: find-untranslated did report errors in $INPUT_DIR"

if ! $I18NDUDE > /dev/null; then
    echo "ERROR: bin/i18ndude without arguments gives an error."
    exit 1
fi
echo "GOOD: bin/i18ndude without arguments gives no error."
