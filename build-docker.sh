#!/bin/bash
docker rm -f lab
docker rmi -f lab
docker build --tag=lab .
docker run -d -p 5000:5000 --name=lab lab