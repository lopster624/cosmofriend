import time
import subprocess
import os
from django.core.management import call_command
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "engine.settings")
django.setup()
while True:
    call_command('cleanup_unused_media', interactive=False)
    call_command('delete_sharelinks')
    time.sleep(60 * 5)
