#!/usr/bin/env bash
NAME=monitor:latest

# build local docker image
docker rmi $NAME
docker build -t $NAME .
