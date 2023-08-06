class AbstractEvents:
    CHOICES = []

    @classmethod
    def as_choices(cls):
        return [(type_name.upper(), type_name) for type_name, _ in cls.CHOICES]
