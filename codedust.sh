#!/bin/bash

pushd "$(dirname "$0")" # Go to script directory

exit_code=0

python3 codedust.py \
    --extension py \
    --extension sh \
    --path . \
    --ignore 'test_codedust.py' \
    --ignore '__pycache__' \
    --config codedust.cfg

if [ $? -ne 0 ]; then
    exit_code=1
fi

popd # Go back to caller directory

exit $exit_code
