from importlib import import_module

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
