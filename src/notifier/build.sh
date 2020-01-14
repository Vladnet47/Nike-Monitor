#!/usr/bin/env bash
NAME=notifier:latest

# build local docker image
docker rmi $NAME
docker build -t $NAME .
