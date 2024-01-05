from django.core.management import execute_from_command_line
from ruamel.yaml import YAML

import os
import sys

CONFIG_FILEPATH = "./config.yaml"

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    project_dir = os.path.join(script_dir, 'bms')
    sys.path.append(project_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bms.settings")

    config = YAML().load(open(CONFIG_FILEPATH))
    host = config['web']['host']
    port = str(config['web']['port'])
    address = host + ':' + port

    execute_from_command_line(['bms/manage.py', 'runserver', address])