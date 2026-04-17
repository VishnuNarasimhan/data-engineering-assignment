import boto3
from botocore.exceptions import BotoCoreError, ClientError
from config import REGION, SQS_ENDPOINT, AWS_ACCESS_KEY, AWS_SECRET_KEY, QUEUE_URL

# Create and return an SQS client with configuration.
def get_sqs_client():
    try:
        return boto3.client(
            "sqs",
            region_name=REGION,
            endpoint_url=SQS_ENDPOINT,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
    except (BotoCoreError, ClientError) as error:
        print("Failed to create SQS client:", error)
        raise

# Receive messages from the configured SQS queue.
def receive_messages():
    try:
        sqs = get_sqs_client()

        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=5
        )

        return response.get("Messages", [])
    except (BotoCoreError, ClientError) as error:
        print("Failed to receive SQS messages:", error)
        return []
