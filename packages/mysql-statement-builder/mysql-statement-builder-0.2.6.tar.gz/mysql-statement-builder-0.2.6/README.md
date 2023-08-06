# MySQL-statement-builder (mysqlsb)
...

## Installation
```pip install mysql-statement-builder```

## Usage
```
import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager

from mysqlsb import MySQLStatementBuilder, FetchType

# Setup a connection pool using the MySQL python connector
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    user='user',
    password='password',
    host='host',
    database='database',
    port='port',
    autocommit=False,
)


# Setup a method for recieving a connection from the connection pool
@contextmanager
def get_connection() -> pooling.PooledMySQLConnection:
    """
    Returns a MySQL connection that can be used for read/write.
    """
    connection = connection_pool.get_connection()
    try:
        yield connection
    finally:
        connection.close()


# Apply mysql-statement-builder to select data from the database
def get_user_from_database(user_id: int):
    with get_connection() as connection:
        mysql_statement = MySQLStatementBuilder(connection)
        user_data = mysql_statement \
            .select('users', ['id', 'username', 'email']) \
            .where('id = %s', [user_id]) \
            .execute(fetch_type=FetchType.FETCH_ONE, dictionary=True)

        if user_data is None:
            raise UserNotFoundException('User could not be found in database')

        user = User(**user_data)  # Unpack results dictionary into e.g. a Pydantic basemodel class
        return user
```