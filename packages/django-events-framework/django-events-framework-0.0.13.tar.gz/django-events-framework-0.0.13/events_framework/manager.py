import logging
from django.db import transaction

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)


class EventsManager:
    def __init__(self):
        self._events_registry = {}

    def register(self, event_model, event_type, handler):
        if handler in self._events_registry:
            logger.info("event handler allready in registry")
            return

        self._events_registry[handler] = {
            "type": event_type,
            "event_model": event_model,
        }

    def process(self):
        for handler, props in self._events_registry.items():
            event_model = props["event_model"]
            event_type = props["type"]
            events_to_process = event_model.objects.filter(
                type=event_type,
                processed=False,
            )

            for event in events_to_process:
                with transaction.atomic():
                    for e in events_to_process.filter(pk=event.pk).select_for_update(
                        skip_locked=True
                    ):
                        try:
                            handler(e)
                            e.processed = True
                            e.save()
                        except Exception as ex:
                            logger.warning(str(ex))
                            e.error = True
                            e.error_message = str(ex)
                            e.processed = True
                            e.save()


manager = EventsManager()
