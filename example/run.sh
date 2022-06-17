#!/bin/bash

# Runs the docker-secrets-deploy example image via docker run

# deployment descriptor
export DCKR_SCRTS_DEPLOY=' \
    {"config": "/config/example.conf", \
     "assign": {"pwd": "ENV_PASSWORD"}} \
'

# run with tabs, carriage returns, new lines and backslashes removed from DCKR_SCRTS_DEPLOY
docker run --rm \
	  -e DCKR_SCRTS_DEPLOY="${DCKR_SCRTS_DEPLOY//[$'\t\r\n\\']}" \
	  -e ENV_PASSWORD="bLupdLr4R2HY" \
          docker-secrets-deploy-example
