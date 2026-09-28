#!/usr/bin/env bash

# script used for manually running all pre-commit hooks
# run this script locally and make sure no hook fails before pushing changes
# test and deploy plans run this script and the whole plan will fail if any hook fails

SCRIPT_PATH=$(readlink -f $0)  # get absolute path of this script

# get absolute path to the parent directory of this script (pycaption/scripts/code_checks)
CODE_CHECKS_DIR=$(dirname $SCRIPT_PATH)

PYCAPTION_DIR=$(dirname $(dirname $CODE_CHECKS_DIR))  # get pycaption absolute path
cd $PYCAPTION_DIR  # cd to pycaption directory

# builds pre-commit environment
docker build . --file="./Dockerfile_precommit" --tag="pycaption_code_checks:latest"

# run pre-commit on all files with all the other arguments passed along to this script
docker run --rm -v $PWD:/pycaption pycaption_code_checks:latest bash -c \
    "pre-commit run --all-files $*"
