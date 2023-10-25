#!/bin/bash

echo "$1"

if [ $1 == "test_py37" -o $1 == "test_py38"  -o $1 == "test_py39"  ]; then
    docker compose up $1
else
  docker compose up test_py39
fi