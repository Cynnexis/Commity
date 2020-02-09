#!/bin/bash

source ~/.bashrc

command=""
if [[ $# == 0 ]]
then
	command="run"
else
	command=$1
fi

output=''
exit_code=0

# Parse command
if [ $command == "run" ]
then
  output=$(python commity.py -r ~/git-test-repo -b getting-started)
  exit_code=$?
elif [ $command == "lint" ]
then
  output=$(yapf -r --diff .)
  exit_code=$?
elif [ $command == "fix lint" ] || [ $command == "lint fix" ]
then
  output=$(yapf -ir .)
  exit_code=$?
elif [ $command == "test" ]
then
  output=$(python -m unittest test/commity-test.py)
  exit_code=$?
fi

echo ::set-output name=output::$output
echo ::set-output name=exit_code::$exit_code
exit $exit_code
