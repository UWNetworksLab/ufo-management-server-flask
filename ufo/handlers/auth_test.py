"""Test auth module functionality (at least what parts can be tested)."""
import datetime
import json
import unittest

import ufo
from ufo import base_test
from ufo.database import models
from ufo.handlers import auth


class AuthTest(base_test.BaseTest):
  """Test auth class functionality."""

  def setUp(self):
    """Setup test app on which to call handlers and db to query."""
    super(AuthTest, self).setUp()
    super(AuthTest, self).setup_config()
    super(AuthTest, self).setup_auth()
    ufo.RECAPTCHA_ENABLED_FOR_APP = True

  def testTurnOffRecaptchaIfRecaptchaWasOnAndTimedOut(self):
    """Test recaptcha turns off if it was on and timed out."""
    start_datetime = datetime.datetime.now()

    # Add some failed attempts to the DB after start datetime.
    expected_count = 3
    for x in range(expected_count):
      models.FailedLoginAttempt.create()

    # Set the config to show recaptcha with an end datetime of now.
    config = ufo.get_user_config()
    config.should_show_recaptcha = True
    config.recaptcha_start_datetime = start_datetime
    config.recaptcha_end_datetime = datetime.datetime.now()
    config.save()

    should_show_recaptcha, failed_attempts_count = auth.determine_if_recaptcha_should_be_turned_on_or_off()

    self.assertFalse(should_show_recaptcha)
    self.assertEquals(expected_count, failed_attempts_count)
    self.assertEquals(0, len(models.FailedLoginAttempt.get_all()))
    config = ufo.get_user_config()
    self.assertFalse(config.should_show_recaptcha)

  def testTurnOnRecaptchaIfRecaptchaWasOnAndFailedAttemptsOverMax(self):
    """Test recaptcha turns on if it was on and went over max failed login."""
    start_datetime = datetime.datetime.now()

    # Add enough failed attempts to the DB after start datetime to hit max.
    for x in range(ufo.MAX_FAILED_LOGINS_BEFORE_RECAPTCHA):
      models.FailedLoginAttempt.create()

    # Set the config to show recaptcha with an end datetime of now.
    config = ufo.get_user_config()
    config.should_show_recaptcha = True
    config.recaptcha_start_datetime = start_datetime
    initial_delta = datetime.timedelta(minutes=5)
    end_datetime = start_datetime + initial_delta
    config.recaptcha_end_datetime = end_datetime
    config.save()
    test_datetime = datetime.datetime.now()

    should_show_recaptcha, failed_attempts_count = auth.determine_if_recaptcha_should_be_turned_on_or_off()
    self.assertTrue(should_show_recaptcha)
    self.assertEquals(ufo.MAX_FAILED_LOGINS_BEFORE_RECAPTCHA,
                      failed_attempts_count)
    self.assertEquals(ufo.MAX_FAILED_LOGINS_BEFORE_RECAPTCHA,
                      len(models.FailedLoginAttempt.get_all()))
    config = ufo.get_user_config()
    self.assertTrue(config.should_show_recaptcha)
    self.assertTrue(config.recaptcha_start_datetime >= test_datetime)
    self.assertTrue(config.recaptcha_end_datetime >= test_datetime)
    new_delta = config.recaptcha_end_datetime - config.recaptcha_start_datetime
    self.assertEquals(2*initial_delta, new_delta)

  def testTurnOnRecaptchaIfRecaptchaWasOffAndFailedAttemptsOverMax(self):
    """Test recaptcha turns on if it was off and went over max failed login."""
    # Add enough failed attempts to the DB after start datetime to hit max.
    for x in range(ufo.MAX_FAILED_LOGINS_BEFORE_RECAPTCHA):
      models.FailedLoginAttempt.create()

    # Set the config to show recaptcha with an end datetime of now.
    config = ufo.get_user_config()
    config.should_show_recaptcha = False
    config.save()
    test_datetime = datetime.datetime.now()

    should_show_recaptcha, failed_attempts_count = auth.determine_if_recaptcha_should_be_turned_on_or_off()
    self.assertTrue(should_show_recaptcha)
    self.assertEquals(ufo.MAX_FAILED_LOGINS_BEFORE_RECAPTCHA,
                      failed_attempts_count)
    self.assertEquals(ufo.MAX_FAILED_LOGINS_BEFORE_RECAPTCHA,
                      len(models.FailedLoginAttempt.get_all()))
    config = ufo.get_user_config()
    self.assertTrue(config.should_show_recaptcha)
    self.assertTrue(config.recaptcha_start_datetime >= test_datetime)
    self.assertTrue(config.recaptcha_end_datetime >= test_datetime)
    new_delta = config.recaptcha_end_datetime - config.recaptcha_start_datetime
    default_delta = datetime.timedelta(
        minutes=auth.INITIAL_RECAPTCHA_TIMEFRAME_MINUTES)
    self.assertEquals(default_delta, new_delta)

  def testRecaptchaStaysOffIfNotConfigured(self):
    """Test recaptcha does not turn on if not configured."""
    # Add enough failed attempts to the DB after start datetime to hit max.
    for x in range(ufo.MAX_FAILED_LOGINS_BEFORE_RECAPTCHA):
      models.FailedLoginAttempt.create()

    # Set the config to show recaptcha with an end datetime of now.
    config = ufo.get_user_config()
    config.should_show_recaptcha = False
    config.save()
    ufo.RECAPTCHA_ENABLED_FOR_APP = False
    test_datetime = datetime.datetime.now()

    should_show_recaptcha, failed_attempts_count = auth.determine_if_recaptcha_should_be_turned_on_or_off()
    self.assertFalse(should_show_recaptcha)
    self.assertEquals(ufo.MAX_FAILED_LOGINS_BEFORE_RECAPTCHA,
                      failed_attempts_count)
    self.assertEquals(ufo.MAX_FAILED_LOGINS_BEFORE_RECAPTCHA,
                      len(models.FailedLoginAttempt.get_all()))
    config = ufo.get_user_config()
    self.assertFalse(config.should_show_recaptcha)



if __name__ == '__main__':
  unittest.main()
