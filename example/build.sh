#!/bin/bash

# Builds the docker-secrets-deploy example image via docker build

scriptdir=$(dirname $(readlink -f $0))

docker build \
	--build-arg DCKR_SCRTS_DEPLOY_TOKEN_USERNAME=${DCKR_SCRTS_DEPLOY_TOKEN_USERNAME} \
	--build-arg DCKR_SCRTS_DEPLOY_TOKEN_PASSWORD=${DCKR_SCRTS_DEPLOY_TOKEN_PASSWORD} \
	-t docker-secrets-deploy-example $scriptdir $1
