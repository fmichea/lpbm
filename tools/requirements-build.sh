#! /bin/sh

for req_in in $(ls requirements/*.in); do
    pip-compile -U --output-file "${req_in/.in/.txt}" "${req_in}"
done
