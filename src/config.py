"""Application configuration values.

This module stores connection settings for local SQS-compatible messaging,
AWS credentials used by the local environment, and PostgreSQL database access.
"""

SQS_ENDPOINT="http://localhost:4566"
QUEUE_URL="http://localhost:4566/000000000000/test-queue"

AWS_ACCESS_KEY="test"
AWS_SECRET_KEY="test"
REGION="ap-south-1"

DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="trips"
DB_USER="admin"
DB_PASSWORD="admin"
