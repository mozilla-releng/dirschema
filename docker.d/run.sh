#!/bin/bash

set +e

test $PRIVATE_KEY
test $APP_ID

GLOBAL_FLAGS=""
CMD_FLAGS=""

if [ -n "$VERBOSE" ]; then
    GLOBAL_FLAGS="-v"
fi
if [ -n "$HOST" ]; then
    CMD_FLAGS="$CMD_FLAGS --host $HOST"
fi
if [ -n "PORT" ]; then
    CMD_FLAGS="$CMD_FLAGS --port $PORT"
fi

exec /usr/local/bin/dirschema $GLOBAL_FLAGS run-github-app $CMD_FLAGS $PRIVATE_KEY $APP_ID
