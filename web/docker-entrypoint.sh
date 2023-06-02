#!/bin/sh

echo "Waiting for PostgreSQL to start..."
./wait-for db:5432 --timeout=60

python3 main.py
