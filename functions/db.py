'''
# Created by collaboration between:
# - [Lanutrix](https://github.com/Lanutrix)
# - [An0nX](https://github.com/An0nX)
'''

import psycopg2
from loguru import logger

class PostgreSQLController:
    @logger.catch
    def __init__(self, host:str="localhost", user:str="postgres", password:str="postgres", database:str="postgres", table_definition:str=None) -> None:
        """
        Initialize a new instance of the class.

        Parameters:
            host (str): The host address of the PostgreSQL server. Default is "localhost".
            user (str): The username for the PostgreSQL server. Default is "postgres".
            password (str): The password for the PostgreSQL server. Default is "postgres".
            database (str): The database name for the PostgreSQL server. Default is "postgres".
            table_definition (str): Optional table definition query to create a table in the database.

        Returns:
            None

        Raises:
            Exception: If there is an error while working with PostgreSQL.
        """
        try:
            self.connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.connection.autocommit = True

            logger.success("PostgreSQL connection established")

            if table_definition:
                with self.connection.cursor() as cursor:
                    cursor.execute(table_definition)
                    logger.success("Table created successfully")
            else:
                logger.debug("No table definition provided")

        except Exception as ex:
            logger.critical("Error while working with PostgreSQL", ex)

    @logger.catch
    def read(self, table: str, columns: str, requirement: str = ""):
        """
        Reads data from a specified table in the database.

        Args:
            table (str): The name of the table to read from.
            columns (str): The columns to select from the table.
            requirement (str, optional): An additional requirement to filter the data. Defaults to "".

        Returns:
            list: A list of tuples representing the result of the query.
        """
        logger.info(f"Reading from table {table}")
        with self.connection.cursor() as cursor:
            requirement = f"WHERE {requirement}" if requirement else ""
            cursor.execute(f"SELECT {columns} FROM {table} {requirement}")
            result = cursor.fetchall()
            logger.debug(f"Read result: {result}")
            return result

    @logger.catch
    def write(self, table: str, columns: str, values: str) -> bool:
        """
        Writes data to a specified table in the database.

        Args:
            table (str): The name of the table to write to.
            columns (str): The columns to insert data into.
            values (str): The values to insert into the columns.

        Returns:
            bool: True if the write operation is successful, False otherwise.
        """
        logger.info(f"Writing to table {table}")
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({values});")
            logger.success(f"Write to table {table} successful")
            return True
        except Exception as ex:
            logger.error(f"Failed to write to {table}: {ex}")
            return False

    @logger.catch
    def update(self, table: str, data: str, requirement: str) -> bool:
        """
        Updates a table in the database with the given data based on the specified requirement.

        Parameters:
            table (str): The name of the table to update.
            data (str): The data to update in the table.
            requirement (str): The requirement to identify the rows to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logger.info(f"Updating table {table}")
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"UPDATE {table} SET {data} WHERE {requirement}")
            logger.success(f"Update to table {table} successful")
            return True
        except Exception as ex:
            logger.error(f"Failed to update {table}: {ex}")
            return False

    @logger.catch
    def delete(self, table: str, requirement: str) -> bool:
        """
        Delete a row from the specified table based on the given requirement.

        Parameters:
            table (str): The name of the table from which to delete the row.
            requirement (str): The requirement that the row must satisfy for deletion.

        Returns:
            bool: True if the deletion is successful, False otherwise.
        """
        logger.info(f"Deleting from table {table}")
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {table} WHERE {requirement}")
            logger.success(f"Deletion from table {table} successful")
            return True
        except Exception as ex:
            logger.error(f"Failed to delete from {table}: {ex}")
            return False

    @logger.catch
    def close(self):
        """
        Close the PostgreSQL connection.

        This function closes the PostgreSQL connection established by the `connect` method.
        It logs the action of closing the connection using the `logger` object.

        Parameters:
        - None

        Returns:
        - None
        """
        logger.info("Closing PostgreSQL connection")
        self.connection.close()
        logger.success("PostgreSQL connection closed")
    
    @logger.catch
    def execute_query(self, query: str):
        """
        Execute a SQL query on the database.

        Parameters:
        - query (str): The SQL query to execute.

        Returns:
        - list: A list of tuples representing the result of the query.
        """
        logger.debug(f"Executing query: {query}")
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                logger.debug(f"Query executed successfully")
                return result
        except psycopg2.ProgrammingError as ex:
            logger.error(f"Failed to execute query: {ex}")
            return None
    