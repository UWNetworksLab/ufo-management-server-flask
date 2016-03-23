"""This module contains the custom exceptions used by the app."""


PLEASE_CONFIGURE_TEXT = 'Please finish configuring this site.'


# TODO: Move the other exceptions here.

class SetupNeeded(Exception):
  code = 500
  message = PLEASE_CONFIGURE_TEXT


class NotLoggedIn(Exception):
  """An exception for when a user in not logged in.

  To be thrown by the decorators listed below."""
  code = 401
  message = 'User is not logged in'


class UnableToSaveToDB(Exception):
  """An exception for when we can not save to DB."""
  code = 500
  message = ('Unable to save to DB.  Check if constraint is violated.')
