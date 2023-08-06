import pandas as pd
import redshift_connector
from redshift_connector import Connection, Cursor


def get_redshift_cursor(host: str, database: str, user: str, password: str) -> Cursor:
    """Get a cursor to the Redshift database.

    Args:
        host (str): The host of the Redshift database
        database (str): The name of the database
        user (str): The user to connect to the database
        password (str): The password to connect to the database

    Returns:
        Cursor: A cursor to the Redshift database
    """
    conn: Connection = redshift_connector.connect(
        host=host, database=database, user=user, password=password
    )
    return conn.cursor()


def get_table_columns_information(cursor: Cursor, redshift_table: str) -> tuple:
    """Get the columns information of the table.

    Args:
        cursor (Cursor): A cursor to the Redshift database
        redshift_table (str): The name of the table

    Returns:
        tuple: A tuple containing the columns information of the table
    """
    cursor.execute(f"SELECT pg_get_cols('{redshift_table}');")
    return cursor.fetchall()


def query_to_dataframe(cursor: Cursor, query: str) -> pd.DataFrame:
    """Execute a query and return the result as a pandas DataFrame.

    Args:
        cursor (Cursor): A cursor to the Redshift database
        query (str): A query to execute

    Returns:
        pd.DataFrame: The result of the query as a pandas DataFrame
    """
    cursor.execute(query)
    return cursor.fetch_dataframe()
