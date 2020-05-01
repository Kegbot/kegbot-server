#!/bin/bash

MAX_ATTEMPTS=60

function getContainerHealth {
  docker inspect --format "{{.State.Health.Status}}" $1
}

function waitContainer {
  attempts=0
  while STATUS=$(getContainerHealth $1); [ $STATUS != "healthy" ]; do 
    if [ $STATUS == "unhealthy" ]; then
      echo "container is unhealthy"
      exit -1
    fi
    echo "container $1: status $STATUS ..."
    lf=$'\n'
    attempts=$[$attempts+1]
    if [ $attempts -ge $MAX_ATTEMPTS ]; then
      echo "Max attempts reached; fail"
      exit -1
    fi
    sleep 1
  done
  echo "Container is up!"
}

waitContainer $1
