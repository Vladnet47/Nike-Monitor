#!/usr/bin/env bash
NAME=management_api:latest

# build local docker image
docker rmi $NAME
docker build -t $NAME .
