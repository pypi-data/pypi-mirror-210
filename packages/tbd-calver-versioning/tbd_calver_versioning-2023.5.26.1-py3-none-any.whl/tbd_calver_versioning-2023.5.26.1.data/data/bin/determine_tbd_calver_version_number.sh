#!/bin/bash

set -e
set -x

# This script will determine the version number of a commit based on the 
# Trunk Based Development branching strategy and a CalVer versioning strategy
#
# The branching strategy assumes that the following branches/branch types exist:
#
#   release/<yyyy.mm.dd>
#   patch/<human-friendly-description>
#   master
#   bug/<human-friendly-description>
#   feature/<human-friendly-description>
#
# We can expect version numbers to resemble the following:
#
#   2022.03.31.release.5
#   2022.03.31.patch.2a00f14b
#   2022.03.31.main.1
#   2022.03.31.feature.2a00f143
#   2022.03.31.bug.2a00f143028f
#
# The build number or SHA will be added based on the branch type. Build numbers 
# will increment with each merge that occurs on a given day.
#

# Collect information from the git client

	GIT_VERSION=$(git --version)
	BRANCH_NAME=$(git branch | grep "*" | awk '{print $2}')
	BRANCH_TYPE=$(echo "${BRANCH_NAME}" | awk -F/ '{print $1}')
	BRANCH_NAME_PART_COUNT=$(echo "${BRANCH_NAME}" | sed 's/\// /g' | wc -w)
	COMMIT_HASH=$(git log -1 --format=format:"%h")
	COMMIT_DATE=$(git log -1 --format="%at" | xargs -I{} date -d @{} +'%Y-%m-%d')
	COMMIT_DATE_PRETTY=$(date -d "${COMMIT_DATE}" +'%Y.%m.%d')
	PREVIOUS_DATE=$(date -d "${COMMIT_DATE} -1 days" +'%Y-%m-%d')
	if [ -z "${MAINLINE_BRANCH}" ]; then
		export MAINLINE_BRANCH=master
	fi

# Determine if we are dealing with a merge commit (likely a merge request or pull request)

	# https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
	SOURCE=${BASH_SOURCE[0]}
	while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
		DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
		SOURCE=$(readlink "$SOURCE")
		[[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
	done
	CURRENT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

	ROOT_DIR=$(dirname $(realpath "$CURRENT_DIR"))

	IS_MERGE_COMMIT=$(bash "${ROOT_DIR}/repo_inspection/determine_if_commit_is_merge_commit.sh")

# Validate the information we collected and raise an exception if something doesnt look right

	if 	[[ "${BRANCH_TYPE}" != "release" ]] && \
		[[ "${BRANCH_TYPE}" != "patch" ]] && \
		[[ "${BRANCH_TYPE}" != "${MAINLINE_BRANCH}" ]] && \
		[[ "${BRANCH_TYPE}" != "bug" ]] && \
		[[ "${BRANCH_TYPE}" != "feature" ]]
	then
		echo "The branch type ${BRANCH_TYPE} is not supported"
		exit 1
	fi
	
	if [[ "${BRANCH_NAME_PART_COUNT}" != 1 && "${BRANCH_NAME_PART_COUNT}" != 2 ]]; then
		echo "The branch name ${BRANCH_NAME} did not have the right number of parts"
		exit 1
	fi

# Collect more information for the edge cases

	# When a commit is made, the commit has parents marking the branches involved
	# Typically, first perent represents the branch where the commit was originally made
	# The first-parent flag allows us to filter out commit/merges which occurred on our branch
	# as opposed to another branch
	
	FIRST_COMMIT=$(git log --pretty=tformat:"%h" --first-parent | tail -n 1)

	# If we are on an integration branch we will consider all merges and commits
	# but if we are on a non-integration branch we will only consider merges and commits
	# that occur after the commit that created the branch. This means we need special logic 
	# for the release branch and master branch.

	if [[ "${BRANCH_TYPE}" == "release" ]]; then
		COMMIT_WHERE_BRANCH_CREATED=$(bash "${ROOT_DIR}/repo_inspection/determine_commit_where_branch_created.sh")	
		MERGES_COUNT=$(git rev-list --first-parent --count ${COMMIT_WHERE_BRANCH_CREATED}..HEAD --merges)
		COMMIT_COUNT=$(git rev-list --first-parent --count ${COMMIT_WHERE_BRANCH_CREATED}..HEAD --no-merges)
		VERSION_COUNT=$((MERGES_COUNT + COMMIT_COUNT + 1)) 
		# Note: We add one because the revlist command above does not include the commit in question
	elif [[ "${BRANCH_TYPE}" == "master" ]]; then
		MERGES_COUNT=$(git rev-list --first-parent --count HEAD --since=${PREVIOUS_DATE} --merges)
		COMMIT_COUNT=$(git rev-list --first-parent --count HEAD --since=${PREVIOUS_DATE} --no-merges)
		VERSION_COUNT=$((MERGES_COUNT + COMMIT_COUNT))
	fi


	# =========================================================
	# Special case #1: Committing directly to mainline or release
	# =========================================================
	# Normally we should not be committing directly to the integration branches (master/release)
	# However there is a special case when we are allowed to have commits appear without merges
	# For master, the initial commit on the branch 
	# For release, when branching from master and inheriting that initial commit

	if [[ "${COMMIT_HASH}" != "${FIRST_COMMIT}" ]]; then
		echo "WARNING: A regular (non-merge) commit is not allowed on a ${BRANCH_TYPE} type branch." >&2
		echo "All commits made to this branch must be merge commits!" >&2
	fi

# Set the version number

	if [[ "${BRANCH_TYPE}" == "bug" || "${BRANCH_TYPE}" == "feature" || "${BRANCH_TYPE}" == "patch" ]]; then
		VERSION_NUMBER="${COMMIT_DATE_PRETTY}.${BRANCH_TYPE}.${COMMIT_HASH}"
	elif [[ "${BRANCH_TYPE}" == "${MAINLINE_BRANCH}" || "${BRANCH_TYPE}" == "release" ]]; then
		# Count the number of merge commits
        VERSION_NUMBER="${COMMIT_DATE_PRETTY}.${BRANCH_TYPE}.${VERSION_COUNT}"
	fi

	VERSION_REGEX="^[0-9]{4}\.[0-9]{2}\.[0-9]{2}\.(release|patch|${MAINLINE_BRANCH}|feature|bug)\.([a-z0-9]{7}|[0-9]+)$"
	VERSION_CHECK=$(echo "${VERSION_NUMBER}" | grep -o -E "${VERSION_REGEX}")

	if [ -z "${VERSION_NUMBER}" ] || [[ "${VERSION_CHECK}" != "${VERSION_NUMBER}" ]]; then
		echo "The version number was not set correctly"
		exit 1
	fi

	echo "${VERSION_NUMBER}"

