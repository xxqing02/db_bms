import pymysql
from django.core.management import execute_from_command_line

import os
import sys
from ruamel.yaml import YAML

CONFIG_FILEPATH = "./config.yaml"

def init_database():
    if not os.path.exists(CONFIG_FILEPATH):
        raise Exception("Config file not exists!")

    config = YAML().load(open(CONFIG_FILEPATH))

    conn = pymysql.connect(
        host=config['database']['host'],
        port=config['database']['port'],
        user=config['database']['user'],
        password=config['database']['password'],
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


def init_project():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    project_dir = os.path.join(script_dir, 'bms')
    sys.path.append(project_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bms.settings")

    execute_from_command_line(['bms/manage.py', 'migrate'])
    execute_from_command_line(['bms/manage.py', 'makemigrations', 'app'])
    execute_from_command_line(['bms/manage.py', 'migrate'])


if __name__ == "__main__":
    init_database()
    init_project()
