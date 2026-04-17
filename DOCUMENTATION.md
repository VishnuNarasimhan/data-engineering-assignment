# ETL Data Pipeline 

## Overview
This project implements a simple ETL pipeline that:
- Consumes messages from AWS SQS (via Localstack)
- Handles mutiple input schemas
- Transforms data into a unified structure
- Stores the processed data in PostgreSQL database
- Deletes messages after successful processing

## Tech Stack
- Python 3
- boto3
- PostgreSQL
- Docker Desktop
- Localstack (SQS Simulation)

## Project Structure
```
.
├── DOCUMENTATION.md
├── docker-compose.yml
├── run.sh
├── Makefile
└── src
    ├── main.py
    ├── consumer.py
    ├── transformer.py
    ├── db.py
    └── config.py
```

## Build Requirements
- Docker & Docker Compose
- Python 3.x
- pip

## Environment Setup
Start the required services (SQS + PostgreSQL):
    `docker compose up -d`

## How to run
- Option 1
    `make run`
- Option 2
    `./run.sh`

## How It Works
- Messages are generated and pushed to SQS
- Consumer reads messages from the queue
- Messages are parsed and validated
- Different schemas (route, locations) are transformed into a unified format
- Data is stored in PostgreSQL
- Successfully porcessed messages are deleted from the queue

## Unified Output Format
```json
{
  "id": 1,
  "mail": "example@gmail.com",
  "name": "Full Name",
  "trip": {
    "departure": "A",
    "destination": "B",
    "start_date": "YYYY-MM-DD HH:MM:SS",
    "end_date": "YYYY-MM-DD HH:MM:SS"
  }
}
```

## Database
- PostgreSQL is configured using Docker
- Table: trips
- Idempotency is ensured using:
    `UNIQUE (id, start_date)`
- Insert Logic:
    `ON CONFLICT DO NOTHING`

## Reliability
- Handles malformed JSON safely
- Supports multiple input schemas
- Ensures idempotency inserts
- Messages are deleted only after successful processing

## Challenges Faced
- Malformed JSON handling: Some messages were invalid. Handled safely using try–except and skipped bad records.
- Multiple input schemas: Messages had different structures (route vs locations). Implemented logic to detect and transform each correctly.
- Race condition: Consumer sometimes ran before messages were available. Resolved by adding a controlled delay after message generation.
- Idempotency: Duplicate records were inserted initially. Fixed using a composite key (id, start_date) with ON CONFLICT DO NOTHING.

## Design Decisions
- Python choosen for simplicity and boto3 support
- Modular structure (consumer, transformer, db)
- PostgreSQL used for structured storage
- Composite key used for idempotency

## Conclusion
This project demonstrates a reliable ETL pipeline with:
- Fault tolerence
- Schema transformation
- Idempotency processing
- Automated execution using scripts


