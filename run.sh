#!/bin/bash

set -e

echo "Starting SQS and PostgreSQL containers..."
docker-compose up -d

echo "Waiting for containers to be ready..."
sleep 5

echo "Generating messages and sending to SQS..."
./message-generators/darwin

echo "Waiting for messages to be available..."
sleep 5

# echo "Installing Python dependencies..."
# pip install boto3 psycopg2-binary > /dev/null 2>&1

echo "Running ETL pipeline..."
python src/main.py

echo "Pipeline execution completed!!. Check db for inserted records."