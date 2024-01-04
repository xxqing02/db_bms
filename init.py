import pymysql
# from django.core.management import call_command
# from django.db import connection

import os
from ruamel.yaml import YAML

CONFIG_FILEPATH = "./config.yaml"

if __name__ == "__main__":
    if not os.path.exists(CONFIG_FILEPATH):
        raise Exception("Config file not exists!")

    config = YAML().load(open(CONFIG_FILEPATH))
    info = config['info']

    conn = pymysql.connect(
        host=info['host'],
        port=info['port'],
        user=info['user'],
        password=info['password'],
        charset="utf8",
    )

    cursor = conn.cursor()

    # Drop database if exists
    query = "drop database if exists bms"
    cursor.execute(query)

    # Create database
    query = "create database bms default charset utf8"
    cursor.execute(query)

    query = "show databases"
    cursor.execute(query)
    print("Databases:")
    for row in cursor.fetchall():
        print(row)

    query = "use bms"
    cursor.execute(query)

    query = "show tables"
    cursor.execute(query)
    print("Tables in bms:")
    for row in cursor.fetchall():
        print(row)
    
    # Quit
    cursor.close()
    conn.close()
    print("Database initialized!")
