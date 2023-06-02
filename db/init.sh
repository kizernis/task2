#!/bin/sh

psql -U postgres -c "CREATE USER $DB_USER_NAME PASSWORD '$(cat /run/secrets/db_password)'"
psql -U postgres -c "CREATE DATABASE $DB_DATABASE_NAME OWNER $DB_USER_NAME"
