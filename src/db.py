"""Database access helpers for storing transformed trip data.

This module opens PostgreSQL connections, creates the destination trips table,
and inserts normalized trip records into the database.
"""

import psycopg2
from config import DB_PORT, DB_NAME, DB_HOST, DB_USER, DB_PASSWORD


def get_connection():
    """Open a new PostgreSQL connection using configured credentials.

    Returns:
        psycopg2.extensions.connection: Active PostgreSQL database connection.

    Raises:
        psycopg2.Error: Raised when the database connection fails.
    """
    try:
        return psycopg2.connect(
            port=DB_PORT,
            database=DB_NAME,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except psycopg2.Error as error:
        print("Database connection error:", error)
        raise


def create_table():
    """Create the trips table in PostgreSQL.

    The table is recreated before use and stores user details, trip endpoints,
    and trip start/end timestamps. Duplicate trips are prevented by a unique
    constraint on the user id and trip start date.

    Raises:
        psycopg2.Error: Raised when table creation fails.
    """
    conn = None
    cur = None

    try:
        # Create the trips table once if it does not already exist.
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS trips (
                id INT,
                mail TEXT,
                name TEXT,
                departure TEXT,
                destination TEXT,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                UNIQUE (id, start_date)
            )
            '''
        )

        conn.commit()
    except psycopg2.Error as error:
        # Undo any partial table changes if PostgreSQL reports an error.
        if conn:
            conn.rollback()
        print("Error while creating trips table:", error)
        raise
    finally:
        # Always close database resources, even when an error occurs.
        if cur:
            cur.close()
        if conn:
            conn.close()


def insert_into_db(data):
    """Insert transformed trip data into the trips table.

    Args:
        data (dict): Normalized trip data returned by the transformer.

    Raises:
        KeyError: Raised when expected user or trip fields are missing.
        psycopg2.Error: Raised when PostgreSQL rejects the insert operation.
    """
    conn = None
    cur = None

    try:
        # Insert the transformed trip data into the trips table.
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            '''
            INSERT INTO trips VALUES (%s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (id, start_date) DO NOTHING
            ''',
            (
                data["id"],
                data["mail"],
                data["name"],
                data["trip"]["departure"],
                data["trip"]["destination"],
                data["trip"]["start_date"],
                data["trip"]["end_date"]
            )
        )

        conn.commit()
    except KeyError as error:
        # Raised when the transformed message is missing an expected field.
        print("Missing trip data field:", error)
        raise
    except psycopg2.Error as error:
        # Roll back failed inserts so the connection is left clean.
        if conn:
            conn.rollback()
        print("Error while inserting trip:", error)
        raise
    finally:
        # Close cursor and connection after every insert attempt.
        if cur:
            cur.close()
        if conn:
            conn.close()

    
