#!/bin/bash

set -e
set -x

# Check params are supplied

	if [ -z "${VERSION_NUMBER}" ]; then
		echo "The version number was not set"
		exit 1
	fi
	if [ -z "${GIT_COMMIT}" ]; then
		echo "The version number was not set"
		exit 1
	fi

# Tag the repo

	TAG_RESULT=$(git tag ${VERSION_NUMBER} ${GIT_COMMIT} 2>&1 || true)
	if [[ ! -z "${TAG_RESULT}" ]] && [[ "${TAG_RESULT}" != *"already exists"* ]]; then
		exit 1
	fi

# Push the tag to the remote repo

	git push --tags

