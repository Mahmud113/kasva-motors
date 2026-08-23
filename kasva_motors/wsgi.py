import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kasva_motors.settings")
application = get_wsgi_application()
