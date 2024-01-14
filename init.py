import pymysql
from django.core.management import execute_from_command_line
from django.conf import settings

import os
from ruamel.yaml import YAML

# CONFIG_FILEPATH = "./config.yaml"

def init_database():
    # if not os.path.exists(CONFIG_FILEPATH):
    #     raise Exception("Config file not exists!")

    # config = YAML().load(open(CONFIG_FILEPATH))

    conn = pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456",
        charset="utf8",
    )

    cursor = conn.cursor()

    # Drop database if exists
    query = "DROP DATABASE IF EXISTS bms"
    cursor.execute(query)

    # Create database
    query = "CREATE DATABASE bms DEFAULT CHARSET utf8"
    cursor.execute(query)
  
    # Quit
    cursor.close()
    conn.close()
    print("Database initialized!")


def init_project():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bms.settings')
    execute_from_command_line(['manage.py', 'makemigrations', 'app'])
    execute_from_command_line(['manage.py', 'migrate'])


if __name__ == "__main__":
    init_database()
    init_project()