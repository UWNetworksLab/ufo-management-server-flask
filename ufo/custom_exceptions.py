"""This module contains the custom exceptions used by the app."""


PLEASE_CONFIGURE_TEXT = 'Please finish configuring this site.'


# TODO: Move the other exceptions here.

class SetupNeeded(Exception):
  code = 500
  message = PLEASE_CONFIGURE_TEXT
