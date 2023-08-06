import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application

from libs.env import load_environ
from translate.core.settings import BASE_DIR

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "translate.core.settings")
dotenv_path = Path(BASE_DIR) / ".env"
load_environ(dotenv_path)

application = get_wsgi_application()
