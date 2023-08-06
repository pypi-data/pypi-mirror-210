#!/bin/bash

#This script will configure the git credential helper to store git credentials locally so that git commands 
#authenticate automatically against a remote. Some solutions natively build in this integration (eg. Azure devops). 
#Some do not (eg. Jenkins and gitlab).

set -e
set -x

# Check the environment variables are set

	if [ -z "${GIT_USERNAME}" ]; then
		echo "The git username was not supplied"
		exit 1
	fi

	if [ -z "${GIT_PASSWORD}" ]; then
		echo "The git password was not supplied"
		exit 1
	fi

	if [ -z "${GIT_URL}" ]; then
		echo "The git url was not supplied"
		exit 1
	fi

# Disect the URL and extract components

    URL_HEAD=$(echo "${GIT_URL}" | grep -o -E 'http[s]?://')
	URL_TAIL=$(echo "${GIT_URL}" | sed -e 's/^.*:\/\///g')
	URL_SERVER=$(echo "${URL_TAIL}" | sed -e 's/\/.*$//g')

# Url encode the necessary components

	ENCODED_URL_SERVER=$( echo "${URL_SERVER}" | python -c "import urllib;print urllib.quote(raw_input())" )
	ENCODED_USERNAME=$( echo "${GIT_USERNAME}" | python -c "import urllib;print urllib.quote(raw_input())" )
    ENCODED_PASSWORD=$( echo "${GIT_PASSWORD}" | python -c "import urllib;print urllib.quote(raw_input())" )

# Construct the string for the credential store

    CREDENTIAL_STRING="${URL_HEAD}${ENCODED_USERNAME}:${ENCODED_PASSWORD}@${ENCODED_URL_SERVER}"

# Add the password if it is not already added to the credential store password file

	if [ ! -f ~/.git-credentials ]; then
		echo "${CREDENTIAL_STRING}" > ~/.git-credentials
	else
		CREDENTIALS_EXIST=$(cat ~/.git-credentials | grep ${CREDENTIAL_STRING} || true)
		if [ -z "${CREDENTIALS_EXIST}" ]; then
			echo "${CREDENTIAL_STRING}" >> ~/.git-credentials
		fi
	fi

# Configure git to use the credential store

	git config credential.helper store
