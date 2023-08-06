#!/bin/bash

#This file will accept an array of file paths and will compare those files paths with the list of modified files being tracked 
#in git for this branch. It does a log of git magic to get this list of files and more importantly to determine the commit 
#where the branch started. Once it has the list of files that have changed it compares that list with the list of triggers 
#and print a list of the files which match the triggers. The triggers are regex patterns and are expected to be defined on the 
#pipelines.

set -e
set -x

# Ensure environment variables are set

	if [ -z "${MAINLINE_BRANCH}" ]; then
		echo "The mainline branch was not set"
		exit 1
	fi

	# TRIGGER_PATTERNS is expected to be a space delimited list of string"

	if [ -z "${TRIGGER_PATTERNS}" ]; then
		echo "The list of trigger patterns was not set"
		exit 1
	fi

# Parse the array

	declare -a TRIGGER_PATTERNS_ARRAY
	read -a TRIGGER_PATTERNS_ARRAY <<< "${TRIGGER_PATTERNS}"

	# Print statement for debugging purposes
        echo "${TRIGGER_PATTERNS_ARRAY[@]}" >&2

        echo "Trigger pattern array length: ${#TRIGGER_PATTERNS_ARRAY[@]}" >&2

# Determine where we are

	# https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
	SOURCE=${BASH_SOURCE[0]}
	while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
		DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
		SOURCE=$(readlink "$SOURCE")
		[[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
	done
	CURRENT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

# Determine if the current branch is a mainline branch or not

        BRANCH_NAME=$(git branch | grep "*" | awk '{print $2}')
        if [ -z "${BRANCH_NAME}" ]; then
		echo "Branch name could not bet determined" >&2
		exit 1
	fi
	if [ "${BRANCH_NAME}" = "${MAINLINE_BRANCH}" ]; then
		IS_MAINLINE="true"
	else
		IS_MAINLINE="false"
	fi

# If this is a mainline branch, determine the commit hash of the previous merge commit
# Otherwise get the previous commit

	if [ "${IS_MAINLINE}" = "true" ]; then
		PREVIOUS_COMMIT_HASH=$(git log --merges "${MAINLINE_BRANCH}" --pretty=oneline | awk '{print $1}' | head -n 1)
	fi
	
	if [ "${IS_MAINLINE}" = "false" ] || [ -z "${PREVIOUS_COMMIT_HASH}" ]; then
		PREVIOUS_COMMIT_HASH=$(git rev-list HEAD~1 | head -n 1)
	fi

# Get a list of files that have changed

	CHANGED_FILES=( $(bash "${CURRENT_DIR}/get_changed_files_since_commit.sh" "${PREVIOUS_COMMIT_HASH}") )

# Check if the changed files match any of ther triggers

	MATCHING_FILE=""
	for TRIGGER_PATTERN in "${TRIGGER_PATTERNS_ARRAY[@]}"
	do
		TRIGGER_PATTERN=$(echo "${TRIGGER_PATTERN}" | tr -d '\047') # Remove wrapped single quotes

		for CHANGED_FILE in "${CHANGED_FILES[@]}"
		do
			TRIGGER_MATCH=$(echo "${CHANGED_FILE}" | grep -o -E "${TRIGGER_PATTERN}" || true)

			if [[ ! -z "${TRIGGER_MATCH}" ]]; then
				echo "Changed file '${CHANGED_FILE}' matched trigger pattern '${TRIGGER_PATTERN}'" >&2
				MATCHING_FILE="${CHANGED_FILE}"
				echo "true"
				exit 0
			fi
		done
	done


	if [ -z "${MATCHING_FILE}" ]; then
		echo "false"
	else
		echo "true"
	fi
