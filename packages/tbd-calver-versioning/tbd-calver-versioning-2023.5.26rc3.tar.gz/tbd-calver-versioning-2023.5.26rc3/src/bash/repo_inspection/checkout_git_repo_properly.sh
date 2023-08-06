#!/bin/bash

set -e
set -x

# This script will fetch all branches and tags fromthe remote and then checkout a branch and reset it to a specific commit
#
# It assumes we have already authenticated as a git user
#

# Retrieve parameters from environment variables	

	if [ -z "${BRANCH_NAME}" ]; then
		echo "The BRANCH_NAME was not supplied"
		exit 1
	fi
        if [ -z "${COMMIT_HASH}" ]; then
			echo "The COMMIT_HASH was not supplied"
			exit 1
        fi
	if [ -z "${MAINLINE_BRANCH}" ]; then
		echo "The MAINLINE_BRANCH was not supplied"
		exit 1
	fi

	if [ -z "${GIT_URL}" ]; then
			echo "The GIT_URL was not supplied attempting to retrieve from repo"
		GIT_URL=$(git remote --v | grep fetch | awk '{print $2}')
		if [ -z "${GIT_URL}" ]; then
			echo "The git url could not be determined"
			exit 1
		fi
    fi

# Configure git so we can pull the branches

	git config --list
	# This command will return non-zero exit code if nothing is currently set
	git config --unset-all remote.origin.fetch || true
	git config --global --unset-all remote.origin.fetch || true
	git config remote.origin.fetch refs/heads/${MAINLINE_BRANCH}:refs/remotes/origin/${MAINLINE_BRANCH}
	git config --add remote.origin.fetch refs/heads/${BRANCH_NAME}:refs/remotes/origin/${BRANCH_NAME}
	git config --list

# Do the checkout


	git fetch --all --tags

	git checkout "${BRANCH_NAME}"
    git reset --hard "${COMMIT_HASH}"
