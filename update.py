import os
import sys

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))

    project_dir = os.path.join(script_dir, 'bms')
    sys.path.append(project_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bms.settings")

    execute_from_command_line(['bms/manage.py', 'makemigrations', 'app'])
    execute_from_command_line(['bms/manage.py', 'migrate'])