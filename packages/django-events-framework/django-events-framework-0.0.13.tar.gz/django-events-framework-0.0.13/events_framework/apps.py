from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EventsManagerConfig(AppConfig):
    name = "events_framework"
    verbose_name = _("Events Framework")
    default = True

    def ready(self) -> None:
        super().ready()
        self.module.autodiscover()
