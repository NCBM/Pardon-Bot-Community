"""
Exceptions
"""


from typing import Optional


class InvalidOperationException(Exception):
    def __init__(self, message: Optional[str] = None):
        if message is None:
            super(
                InvalidOperationException, self
            ).__init__("Invalid Operation.")
        else:
            super(
                InvalidOperationException, self
            ).__init__("Invalid Operation: {}".format(message))
