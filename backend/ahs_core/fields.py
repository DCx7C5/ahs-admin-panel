from django.db.models import CharField


class NameField(CharField):
    """
    Custom field that behaves like CharField but also validates a minimum character length.
    """
    def __init__(self, *args, **kwargs):
        self.min_length = kwargs.pop('min_length', None)  # Extract the minimum length parameter
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        """
        Perform validation for the minimum length and call the base class validation.
        """
        if self.min_length is not None and len(value) < self.min_length:
            raise ValueError(
                f"The value for {self.attname} must be at least {self.min_length} characters long."
            )
        # Call the parent class's validate() method
        super().validate(value, model_instance)


class EnumField(CharField):
    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        kwargs.setdefault('max_length', 32)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Add the enum argument so migrations work!
        kwargs['enum'] = self.enum
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.enum(value)

    def to_python(self, value):
        if isinstance(value, self.enum) or value is None:
            return value
        return self.enum(value)

    def get_prep_value(self, value):
        if isinstance(value, self.enum):
            return value.value
        return value
