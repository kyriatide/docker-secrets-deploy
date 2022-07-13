#!/bin/bash

# Builds the docker-secrets-deploy example image via docker build

scriptdir=$(dirname $(readlink -f $0))

docker build -t kyriatide/docker-secrets-deploy-example $scriptdir $1
