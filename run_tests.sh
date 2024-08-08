#!/bin/bash
DOCKER_CMD="docker compose -p pycaption"

SERVICE="test_py312"

if [ "$@" ]; then
  if [ "$1" == "test_py38" ]  || [ "$1" == "test_py39"  ] ||
  [ "$1" == "test_py310" ] || [ "$1" == "test_py311" ] || [ "$1" == "test_py312" ]; then
    SERVICE="$1"
  fi
fi

$DOCKER_CMD build "$SERVICE"

function cleanup {
    echo "Cleaning up ..."
    $DOCKER_CMD down && $DOCKER_CMD rm -fv
}

$DOCKER_CMD run --rm "$SERVICE"

if [ $? != 0 ]; then
  cleanup
  exit 1
else
  cleanup
fi


