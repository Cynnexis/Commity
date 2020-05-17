#!/bin/bash

if [ -f "~/.bashrc" ]; then
	source ~/.bashrc
fi

command=""
if [[ $# == 0 ]]
then
	command="run"
else
	command=$1
fi

if [[ $USE_GIT = "1" || $USE_GIT = "true" ]]; then
	mapfile -t PYTHON_DIRS < <(git diff --cached --name-status | awk -e '$1 != "D" && $2 ~ /\.py$/ {print $2}')
	if [[ ${#PYTHON_DIRS[@]} = 0 ]]; then
		echo "No changes detected in the .py files. Try to detect the whole project."
	fi
else
	declare -a PYTHON_DIRS=()
fi

if [[ ${#PYTHON_DIRS[@]} = 0 ]]; then
	PYTHON_DIRS=(./*.py chatbotutil/ test/ routes/ datablender/ data/)
fi

function print_yapf_tips() {
	echo "If you add a new directory to the project, or create a Python file in a directory that didn't contain any scritps, please make sur that the directory is added to the following YAPF commands:"
	echo " * In ./docker-entrypoint.sh, the variable PYTHON_DIRS must contain all directories that have Python scripts."
	echo " * In ./.git/hooks/pre-commit must have the specified directories as well, at two different places."
	echo ''
	echo "Please update those elements if necessary."
}

exit_code=0

# Parse command
if [ $command == "run" ]
then
	echo "${@:2}"
	python commity.py "${@:2}"
	exit_code=$?
elif [[ $command = "lint" ]]; then
	if [[ $USE_GIT != "1" && $USE_GIT != "true" ]]; then
		print_yapf_tips
	fi
	echo "Running lint..."
	begin=$(date +%s)
	yapf -r --diff "${PYTHON_DIRS[@]}"
	exit_code=$?
	end=$(date +%s)
	echo "Time elapsed to run lint: $((end - begin))s"
elif [[ $command = "fix lint" || $command = "fix-lint" || $command = "lint fix" || $command = "lint-fix" ]]; then
	if [[ $USE_GIT != "1" && $USE_GIT != "true" ]]; then
		print_yapf_tips
	fi
	echo "Running fix-lint..."
	begin=$(date +%s)
	yapf -ir "${PYTHON_DIRS[@]}"
	exit_code=$?
	end=$(date +%s)
	echo "Time elapsed to run lint and fix syntax: $((end - begin))s"
elif [ $command == "test" ]
then
	echo "Covering Python code..."
	begin=$(date +%s)
	coverage run --source="$(pwd)" -m unittest discover --failfast -p "*_test.py" -v
	exit_code=$?
	coverage report --include="$(pwd)/*" -m
	end=$(date +%s)
else
	echo -e "Couldn't interpret command '$command'.\All arguments: $*"
	exit 1
fi

echo "$exit_code"
exit $exit_code
