"""Run the trip processing pipeline.

This module coordinates message consumption from SQS, JSON parsing, trip
transformation, database insertion, and deletion of successfully processed
messages from the queue.
"""

from consumer import get_sqs_client, receive_messages
from transformer import parse_message, transform
from config import QUEUE_URL
from db import create_table, insert_into_db


def delete_message(sqs, receipt_handle):
    """Delete a processed message from the configured SQS queue.

    Args:
        sqs: SQS client used to delete the message.
        receipt_handle (str): Receipt handle for the message to delete.

    Returns:
        bool: True when the message is deleted successfully, otherwise False.
    """
    try:
        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=receipt_handle
        )
        return True
    except Exception as error:
        print("FAILED TO DELETE MESSAGE:", error)
        return False


def run_pipeline():
    """Run one batch of the trip processing pipeline.

    The pipeline receives messages from SQS, parses each message body,
    transforms supported trip schemas, inserts valid records into PostgreSQL,
    and deletes messages only after a successful database insert.
    """
    # Ensure the destination table exists before processing messages.
    create_table()

    # Connect to SQS and fetch a batch of messages.
    try:
        sqs = get_sqs_client()
        messages = receive_messages()
    except Exception as error:
        print("FAILED TO RECEIVE MESSAGES:", error)
        return

    for msg in messages:
        # Each SQS message should include the raw body and receipt handle.
        try:
            raw = msg["Body"]
            receipt_handle = msg["ReceiptHandle"]
        except KeyError as error:
            print("SKIPPING MESSAGE WITH MISSING FIELD:", error)
            continue

        # Convert the raw JSON string into a Python dictionary.
        try:
            data = parse_message(raw)
            if not data:
                delete_message(sqs, receipt_handle)  # Remove unsupported messages from the queue.
                continue
        except Exception as error:
            print("FAILED TO PARSE MESSAGE:", error)
            continue
        
        # Normalize supported message schemas into the DB format.
        try:
            transformed = transform(data)
            if not transformed:
                delete_message(sqs, receipt_handle)  # Remove unsupported messages from the queue.      
                continue
        except Exception as error:
            print("FAILED TO TRANSFORM MESSAGE:", error)
            continue

        # Keep the message in the queue if saving to DB fails.
        try:
            insert_into_db(transformed)
        except Exception as error:
            print("FAILED TO INSERT INTO DB:", error)
            continue

        # Remove the message from SQS after successful DB insert.
        delete_message(sqs, receipt_handle)

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as error:
        print("PIPELINE FAILED:", error)
