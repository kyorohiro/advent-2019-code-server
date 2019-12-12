#!/bin/sh

"${mysql[@]}" < /docker-entrypoint-initdb.d/001_setup.sql_