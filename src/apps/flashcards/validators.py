import os
from django.core.exceptions import ValidationError


def validate_style_filetype(value):
    if not (filetype := os.path.splitext(value.name)[1].lower()) == ".svg":
        raise ValidationError(
            f"Only SVGs can be used as flashcard templates. \"{filetype}\" is not supported."
        )
