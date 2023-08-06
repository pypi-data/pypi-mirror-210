#!/bin/bash

#This file will get a list of files that have changed in any of the git commits that exist on the branch, since the branch was created.

set -e
set -x

# Ensure required variables are set

	if [ -z "${MAINLINE_BRANCH}" ]; then
	        echo "The mainline branch was not set"
		exit 1
	fi

# Set the current directory

	# https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
	SOURCE=${BASH_SOURCE[0]}
	while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
		DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
		SOURCE=$(readlink "$SOURCE")
		[[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
	done
	CURRENT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

# Determine the commit where this branch originally deviated from the mainline branch

	COMMIT_HASH=$(bash "${CURRENT_DIR}/determine_commit_where_branch_created.sh")

	if [ -z "${COMMIT_HASH}" ]; then
	        echo "The commit hash where the branch wascreated could not be determined"
	        exit 1
	fi

# Get a list of files which changed after this commit

	CHANGED_FILES=$(bash "${CURRENT_DIR}/get_changed_files_since_commit.sh" "${COMMIT_HASH}")
	echo "${CHANGED_FILES}"
