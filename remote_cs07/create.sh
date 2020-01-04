#!/bin/bash

password=$1
docker-compose build
docker-compose run app -d -e PASSEORD=${password}




