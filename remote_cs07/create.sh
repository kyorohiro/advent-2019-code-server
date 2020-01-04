#!/bin/bash

password=$1
sed -e "s/dummy_password/${password}/g" docker-compose.yml > docker-compose.yml
"PASSEORD=${password}"

docker-compose build
docker-compose up -d




