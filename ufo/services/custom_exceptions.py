"""This module contains the custom exceptions used by the app."""


PLEASE_CONFIGURE_TEXT = 'Please finish configuring this site.'


# TODO: Move the other exceptions here.
# TODO: Extract these messages for i18n (possibly to resources).

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
  message = ('Unable to save to DB. Check if constraint is violated.')


class AttemptToRemoveLastAdmin(Exception):
  """An exception for when the user attempts to remove the only admin."""
  code = 409
  message = ('Can\'t delete the last admin in the database. Add another ' +
             'admin then try to delete this one again.')
