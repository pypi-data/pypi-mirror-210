#!/bin/bash

# https://stackoverflow.com/questions/3824050/telling-if-a-git-commit-is-a-merge-revert-commit

set -e
set -x

COMMIT_HASH=$1
if [ -z "${COMMIT_HASH}" ]; then
	COMMIT_HASH="HEAD"
fi

# We are assuming we have checked out the branch of interest

BRANCH_PARENT_COUNT=$(git cat-file -p "${COMMIT_HASH}" | grep -e "^parent" | wc -l)
if [ "${BRANCH_PARENT_COUNT}" -le 1 ]; then
	IS_MERGE_COMMIT="false"
elif [ "${BRANCH_PARENT_COUNT}" -gt 1 ]; then
	IS_MERGE_COMMIT="true"
fi

echo "${IS_MERGE_COMMIT}"
