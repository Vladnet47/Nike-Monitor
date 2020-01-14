#!/usr/bin/env bash
NAME=validator:latest

# build local docker image
docker rmi $NAME
docker build -t $NAME .
