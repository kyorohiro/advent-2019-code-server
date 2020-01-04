#!/bin/bash

password=$1
docker-compose build
docker-compose run  -d -e "PASSEORD=${password}" app




