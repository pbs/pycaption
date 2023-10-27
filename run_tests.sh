#!/bin/bash -eux

DOCKER_CMD="docker-compose -p pycaption"

SERVICE="test_py39"

if [ "$@" ]; then
  if [ "$1" == "test_py37" ] || [ "$1" == "test_py38" ]  || [ "$1" == "test_py39"  ]; then
    SERVICE="$1"
  fi
fi

$DOCKER_CMD build "$SERVICE"

function cleanup {
    echo "Cleaning up ..."
    $DOCKER_CMD down && $DOCKER_CMD rm -fv
}

$DOCKER_CMD run --rm "$SERVICE"

cleanup
