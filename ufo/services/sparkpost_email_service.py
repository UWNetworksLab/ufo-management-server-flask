"""The module for sending an email out for account recovery."""

from sparkpost import SparkPost
import os


class SparkpostEmail(object):
  """Sends an email using the sparkpost API."""

  RECOVERY_SUBJECT = 'Admin Account Recovery'
  RECOVERY_MESSAGE_START = '<html><body><p>Here\s your new password: '
  RECOVERY_MESSAGE_END = '</p></body></html>'
  FROM_USERNAME = 'test'

  def send_recovery_email(self, recipient, new_password):
    """Send out a recovery email when an admin loses their password.

    Args:
      recipient: An admin's email address as a string.
      new_password: A string for the new password to be sent out.
    """
    sparky = SparkPost()
    domain = os.environ.get('SPARKPOST_SANDBOX_DOMAIN')
    from_email = SparkpostEmail.FROM_USERNAME + '@' + domain
    message = RECOVERY_MESSAGE_START + new_password + RECOVERY_MESSAGE_END
    subject_line = domain + ' ' + RECOVERY_SUBJECT

    response = sparky.transmission.send(
        recipients=[recipient],
        html=message,
        from_email=from_email,
        subject=subject_line
    )
