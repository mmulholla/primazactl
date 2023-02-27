#!/usr/bin/env bash

. ./hack/check-python/prepare-env.sh

# run the pyflakes for all files that are provided in $1
function check_files() {
    for source in $1
    do
        echo "$source"
        "$PYTHON_VENV_DIR/bin/pyflakes" "$source"
        exit=$?
        if [ $exit -eq 0 ]
        then
            echo "    Pass"
            (( pass++ ))
        elif [ $exit -eq 2 ]
        then
            echo "    Illegal usage (should not happen)"
            exit 2
        else
            echo "    Fail"
            (( fail++ ))
        fi
    done
}


echo "----------------------------------------------------"
echo "Checking source files for common errors"
echo "in the following directories:"
echo "$directories"
echo "----------------------------------------------------"
echo

[ "$NOVENV" == "1" ] || prepare_venv || exit 1

# checks for the whole directories
for directory in $directories
do
    pwd
    files=$(find "$directory" -path "$PYTHON_VENV_DIR" -prune -o -name '*.py' -print)

    check_files "$files"
done


if [ "$fail" -eq 0 ]
then
    echo "All checks passed for $pass source files"
else
    (( total=pass+fail ))
    echo "$fail source files out of $total files needs to be checked and fixed"
    exit 1
fi
