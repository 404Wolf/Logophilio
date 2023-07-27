import os
from django.core.exceptions import ValidationError


def validate_style_filetype(value):
    if not os.path.splitext(value.name)[1] == "svg":
        raise ValidationError("Only SVGs can be used as flashcard templates.")
