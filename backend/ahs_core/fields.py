from django.core.exceptions import ValidationError
from django.db.models import CharField, IntegerField


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

