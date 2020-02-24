#!/bin/bash
set -ex

if [ -n "${DOCKER_REGISTRY_HOST}" ]; then

    docker tag italiangrid/storm-load-testsuite ${DOCKER_REGISTRY_HOST}/italiangrid/storm-load-testsuite
    docker push ${DOCKER_REGISTRY_HOST}/italiangrid/storm-load-testsuite

fi
