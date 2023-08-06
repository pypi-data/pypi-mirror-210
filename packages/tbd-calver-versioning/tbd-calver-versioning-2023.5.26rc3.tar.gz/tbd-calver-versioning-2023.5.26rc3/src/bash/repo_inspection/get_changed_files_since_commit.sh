#!/bin/bash

# This script will do git magic to get a list of all the files that have changed since a given commit
# It assumes we have already checked out the branch which contains the commit history we will review
#
# Note: We can think of a commit as a state. So the list of changed files is exclusive, it does not 
# include the files that are changed as part of the first commit. We would need the previous commit
# in that case.
#

set -e
set -x

if [ -z "${COMMIT_HASH}" ]; then
	echo "A commit hash was not provided"
	exit 1
fi

git diff --name-only "${COMMIT_HASH}"~
