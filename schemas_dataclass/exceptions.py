# -*- coding: utf-8 -*-


class ValidationError(Exception):
    """Validation error exception"""

    def __init__(self, message, field_name=None, path=None):
        self.message = message
        self.field_name = field_name
        self.path = path or []
        super(ValidationError, self).__init__(
            ": ".join(self.path + [message]) if self.path else message
        )
