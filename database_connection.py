import mysql.connector


def connect_to_database():
    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="wms"
    )

    # Create a cursor
    c = conn.cursor()

    return conn, c


def close_connection(conn):
    if conn.is_connected():
        conn.close()
