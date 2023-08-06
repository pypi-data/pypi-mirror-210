"""Utility functions/classes for interacting with a MySQL database.
"""

import mysql.connector
import csv

def clean_headers(headers):
    """Accepts list of headers and returns list with illegal characters removed.

    Args:
        headers (list): List of strings.

    Returns:
        list: List of strings with MySQL illegal characters removed.
    """
    cleaned_headers = []
    for header in headers:
        cleaned_headers.append(
            header.replace("/","")\
                .replace("\\","")\
                    .replace("(","")\
                        .replace(")","")
            )
    return cleaned_headers


def get_column_type(values):
    """Returns the MySQL data type that can hold all values in the given list.

    Args:
        values (list): A list of mixed-type values.

    Returns:
        str: The MySQL data type that can hold all values in the given list.
    """

    # Get the list of all data types in values
    data_types_list = [get_value_type(value) for value in values]

    # Find the narrowest data type in the set.
    data_types_set = set(data_types_list)

    if len(data_types_set) == 1:
        return data_types_set.pop()
    if "VARCHAR(255)" in data_types_set:
        return "VARCHAR(255)"
    if "FLOAT" in data_types_set:
        return "FLOAT"
    if "INT" in data_types_set:
        return "INT"
    return "TINYINT"


def get_value_type(value):
    """Returns the MySQL data type that can hold the given value.

    Args:
        value (str): The value to get the data type for.

    Returns:
        str: The MySQL data type that can hold the given value.
    """

    if value in ("0","1"):
        return "TINYINT"
    try:
        int(value)
        return "INT"
    except ValueError:
        try:
            float(value)
            return "FLOAT"
        except ValueError as exc:
            length = len(value)
            if length <= 255:
                return "VARCHAR(255)"
            if length <= 65535:
                return "TEXT"
            if length <= 16777215:
                return "MEDIUMTEXT"
            if length <= 4294967295:
                return "LONGTEXT"
            raise ValueError(
                f"Length of value ({length}) exceeds even LONGTEXT.") from exc


class CSVObject:
    """Wrapper object that facilitates interacting with a CSV.
    """
    def __init__(self, csv_path):
        self.headers = []
        self.rows = []
        self.columns = []
        self.clean_headers = []
        with open(csv_path, "r", encoding="UTF8") as csv_file:
            reader = csv.reader(csv_file)
            self.headers = next(reader)
            self.rows = list(reader)
        for i in range(0, len(self.headers)):
            column = []
            for row in self.rows:
                column.append(row[i])
            self.columns.append(column)
        self.clean_headers = clean_headers(self.headers)


class DBConnection:
    """Wrapper class to abstract away some basic MySQL functions.
    """
    def __init__(self,
                 db_hostname,
                 db_username,
                 db_password,
                 db_schema,
                 db_port):
        self.connection = mysql.connector.connect(
            host=db_hostname,
            user=db_username,
            password=db_password,
            database=db_schema,
            port=db_port
        )
        self.cursor = self.connection.cursor()


    def __str__(self):
        return f"DBConnection:\
            hostname={self.db_hostname},\
            username={self.db_username},\
            schema={self.db_schema}"


    def close_connection(self):
        self.connection.close()


    def insert(self, table, columns, values):
        """Inserts rows into a table.

        Args:
            table (str): The name of the table to insert into.
            columns (list): List of strings representing columns to insert into.
            values (list): List of values to insert into the columns.

        Returns:
            int: The number of rows inserted.
        """

        # Build the SQL statement
        sql = f"INSERT INTO {table} ({columns}) VALUES ({', '.join(values)})"


        # Execute the SQL statement
        self.cursor.execute(sql, values)

        # Commit the changes
        self.connection.commit()

        return self.cursor.rowcount

    def drop_table(self, table):
        """Drops a table.

        Args:
            table (str): The name of the table to drop.

        Returns:
            None
        """

        # Build the SQL statement
        sql = f"DROP TABLE {table}"

        # Execute the SQL statement
        self.cursor.execute(sql)

        # Commit the changes
        self.connection.commit()

    def create_table(self, table, columns, key):
        """Creates a table.

        Args:
            table (str): The name of the table to create.
            columns (list): List of tuples (column_name, column_data_type).
            key (int): Index of column to designate as primary key.

        Returns:
            None
        """

        # Build the SQL statement
        columns_string = ""
        for column in columns:
            columns_string.join(f"{column[0]} {column[1]}, ")
        key_string = columns[key][0]
        sql = f"CREATE TABLE {table} \
            ({columns_string}PRIMARY KEY ({key_string}))"

        # Execute the SQL statement
        self.cursor.execute(sql)

        # Commit the changes
        self.connection.commit()

    def import_csv(self, csv_file, table):
        """Imports a CSV file into a table.

        Args:
            csv_file (str): The path to the CSV file to import.
            table (str): The name of the table to import the CSV file into.

        Returns:
            None
        """

        # Wrap CSV in CSVObject class
        csv_object = CSVObject(csv_file)
        # Determine data type of columns
        header_data_types = [
            get_column_type(column) for column in csv_object.columns
        ]
        # Create list of tuples with column name and data type
        sql_columns = zip(csv_object.clean_headers, header_data_types)

        # Create the table if it doesn't exist
        if not self.table_exists(table):
            self.create_table(table, sql_columns, 0)

        # Insert the rows into the table
        for row in csv_object.rows:
            self.insert(table, csv_object.clean_headers, row)

    def table_exists(self, table):
        """Checks if a table exists.

        Args:
            table (str): The name of the table to check.

        Returns:
            bool: True if the table exists, False otherwise.
        """

        # Build the SQL statement
        sql = f"SELECT 1 FROM information_schema.tables \
            WHERE table_name = '{table}'"

        # Execute the SQL statement
        self.cursor.execute(sql)

        # Check the results
        return self.cursor.fetchone() is not None
