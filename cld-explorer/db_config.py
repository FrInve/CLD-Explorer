import mysql.connector
from mysql.connector import Error

import mysql.connector
from mysql.connector import Error

db_config = {
    # 'host': 'mysql',
    "host": "mysql",
    "port": "3306",
    "user": "app",
    "password": "3utoeZVN!",
    "database": "cld",
}


def get_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
