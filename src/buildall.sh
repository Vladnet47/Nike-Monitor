#!/usr/bin/env bash
pushd ./monitor
./build.sh
popd
pushd ./validator
./build.sh
popd
pushd ./notifier
./build.sh
popd
pushd ./management_api
./build.sh
popd
