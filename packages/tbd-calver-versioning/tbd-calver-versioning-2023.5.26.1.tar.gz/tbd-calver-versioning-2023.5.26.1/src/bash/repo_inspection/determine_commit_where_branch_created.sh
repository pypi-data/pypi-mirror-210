#!/bin/bash

# Overview:
#     This script will do some git-magic to find the first commit on a branch
#     This magic is done using the git rev-list command (which is not subject to ref log expiration)
#
# Explanation:
#     We basically get a list of commits on the mainline/integration branch and a list of commits on our non-mainline
#     We then diff the lists to generate a list of commits that are in the non-mainline but not mainline
#     We then take the last item (earliers) from this list
#
# Assumptions:
#     This command script assumes you are currently checked out on a branch
#
# Credits:
#     https://stackoverflow.com/questions/1527234/finding-a-branch-point-with-git

set -e
set -x

# Ensure environment variables are set

	if [ -z "${MAINLINE_BRANCH}" ]; then
		echo "The mainline branch name was not set."
		exit 1
	fi

# Do some magic to diff the two revision lists

	FISRT_COMMIT_ON_BRANCH=$( diff --old-line-format='' --new-line-format='' \
		<(git rev-list --first-parent "${1:-${MAINLINE_BRANCH}}") \
	        <(git rev-list --first-parent "${2:-HEAD}") | head -1)

	echo "${FISRT_COMMIT_ON_BRANCH=$}"

