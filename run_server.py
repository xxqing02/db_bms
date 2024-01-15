from django.core.management import execute_from_command_line
from django.conf import settings
from ruamel.yaml import YAML
import os


CONFIG_FILEPATH = "./config.yaml"

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bms.settings')
    
    config = YAML().load(open(CONFIG_FILEPATH))
    host = config['web']['host']
    port = str(config['web']['port'])
    execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])
