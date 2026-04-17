from consumer import get_sqs_client, receive_messages
from transformer import parse_message, transform
from config import QUEUE_URL
from db import create_table ,insert_into_db

# Ensure the destination table exists before processing messages.
create_table()

# Delete a message only after it has been processed and saved successfully.
def delete_message(sqs, receipt_handle):
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

        # print("RAW: ", raw)

        # Convert the raw JSON string into a Python dictionary.
        try:
            data = parse_message(raw)
            if not data:
                # print("SKIPPING MALFORMED")
                continue
        except Exception as error:
            print("FAILED TO PARSE MESSAGE:", error)
            continue
        
        # Normalize supported message schemas into the DB format.
        try:
            transformed = transform(data)
            if not transformed:
                # print("UNKNOWN SCHEMA")
                continue
        except Exception as error:
            print("FAILED TO TRANSFORM MESSAGE:", error)
            continue

        #print("TRANSFORMED: ", transformed)

        # Keep the message in the queue if saving to DB fails.
        try:
            insert_into_db(transformed)
            # print("INSERTED INTO DB")
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
