#!/bin/bash

password=$1
git checkout HEAD docker-compose.yml
sed -i "s/dummy_password/${password}/g" docker-compose.yml
docker-compose build
docker-compose up -d

