#!/usr/bin/env sh

set -e

if [ ! -e ../shinymdc ]; then
    echo "error: run from 'test' directory"
    exit 1
fi

mkdir -p samples

for templatef in ../shinymdc/templates/*.tex; do
    template=$(basename "${templatef}" ".tex")
    (set -x; shinymdc -i main.md -o samples/${template}.pdf -t ${template} -cq)
done
