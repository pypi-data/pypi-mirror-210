from django import VERSION
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

if VERSION[0] == 2:
    from jsonfield import JSONField
else:
    from django.db.models.fields.json import JSONField


class EventModel(models.Model):
    date = models.DateTimeField(
        _("Date"),
        default=timezone.now,
        editable=False,
    )

    parameters = JSONField(
        _("Parameters"),
        blank=True,
        default=dict,
    )

    processed = models.BooleanField(
        _("Proccesed"),
        default=False,
    )

    error = models.BooleanField(
        _("Has error?"),
        default=False,
    )

    error_message = models.TextField(_("Error message"), null=True, blank=True, default=None)

    class Meta:
        abstract = True
        ordering = ("date",)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.type!r})"

