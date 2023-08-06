from importlib import import_module

import django
from django.conf import settings


def autodiscover():
    if not hasattr(settings, "EVENT_APPS"):
        return

    if not isinstance(settings.EVENT_APPS, list):
        raise Exception("EVENT_APPS should be a list")

    for app in settings.EVENT_APPS:
        # load processors
        try:
            import_module("%s.%s" % (app, "events.processors"))
        except Exception as e:
            print(e)


# backwards compatibility with Django 2.*
if django.VERSION < (3, 2):
    default_app_config = "events_framework.apps.EventsManagerConfig"
