"""Module representing the error page's page object & functionalities."""

from selenium.webdriver.common.by import By

from base_driver import BaseDriver


class ErrorPage(BaseDriver):
  """Error page's page object and functionalities."""

  # pylint: disable=too-few-public-methods

  ERROR_CODE_ELEMENT = (By.ID, 'errorCode')
  ERROR_DESCRIPTION_ELEMENT = (By.ID, 'errorDescription')
