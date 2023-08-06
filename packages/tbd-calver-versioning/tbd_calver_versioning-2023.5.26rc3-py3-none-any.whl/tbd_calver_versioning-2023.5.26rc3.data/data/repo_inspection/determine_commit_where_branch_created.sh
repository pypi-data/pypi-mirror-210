#!/bin/bash

set -e
set -x

# Ensure required variables are set

	if [ -z "${MAINLINE_BRANCH}" ]; then
		echo "The mainline branch was not set. Please set the MAINLINE_BRANCH variable."
		exit 1
	fi

# Determine where we are

	CURRENT_DIR=$(realpath $(dirname $0))
	CURRENT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


# Inspect the repo

	FIRST_COMMIT_ON_BRANCH=$(bash "${CURRENT_DIR}/determine_first_commit_on_branch.sh" )
	if [ -z "${FIRST_COMMIT_ON_BRANCH}" ]; then
		echo "The commit hash could not be determined"
		exit 1
	fi

	#COMMIT_WHERE_BRANCH_STARTED=$(git rev-list "${FIRST_COMMIT_ON_BRANCH}"~1 | head -n 1)
	COMMIT_WHERE_BRANCH_STARTED=$(git rev-list "${FIRST_COMMIT_ON_BRANCH}..HEAD" | tail -n 1)
	
	if [ -z "${COMMIT_WHERE_BRANCH_STARTED}" ]; then
	        echo "The commit hash could not be determined"
	        exit 1
	fi

# Return the result to stdout

	echo "${COMMIT_WHERE_BRANCH_STARTED}"
