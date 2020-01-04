#!/bin/bash

password=$1
sed -i "s/dummy_password/${password}/g" docker-compose.yml

docker-compose build
docker-compose up -d




