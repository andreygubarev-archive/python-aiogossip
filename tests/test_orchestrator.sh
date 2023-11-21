#!/usr/bin/env bash

set -e

trap "exit" INT TERM ERR
trap "kill 0" EXIT

pushd $WORKSPACE/src
PORT=40000 python3 -m aiogossip.peer &
PORT=40001 SEED=127.0.0.1:40000 python3 -m aiogossip.peer &
PORT=40002 SEED=127.0.0.1:40000 python3 -m aiogossip.peer &
popd

wait
