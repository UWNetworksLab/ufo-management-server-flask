"""Module representing the error notification page object & functionalities."""

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base_driver import BaseDriver
from login_page import LoginPage


class ErrorNotification(BaseDriver):
  """Error notification page object and functionalities."""

  ERROR_NOTIFICATION_ELEMENT = (By.ID, 'error-notification')
  ERROR_NOTIFICATION_DIALOG = (By.ID, 'errorNotificationDialog')
  ERROR_NOTIFICATION_CLOSE_BUTTON = (By.ID, 'errorNotificationCloseButton')
  ERROR_MESSAGE_ELEMENT = (By.ID, 'errorMessage')


  def is_present(self):
    """Whether the error notification element is present on the page.

    Returns: boolean, true if present, else false
    """
    try:
      self.GetElement(self.ERROR_NOTIFICATION_ELEMENT)
    except NoSuchElementException:
      return False
    return True

  def is_displayed(self):
    """Whether the error notification is displayed (i.e. visible) on the page.

    Returns: boolean, true if present, else false
    """
    error_notification_dialog = self.GetElement(self.ERROR_NOTIFICATION_DIALOG)
    if error_notification_dialog.is_displayed():
      return True
    return False

  def has_error_message(self, message):
    """Whether the specified message is present in the error notification.

    Returns: boolean, true if present, else false
    """
    is_present = EC.text_to_be_present_in_element(self.ERROR_MESSAGE_ELEMENT,
                                                  message)
    if is_present is False:
      return False
    return True

  def close(self):
    """Close the error notification, so that it's not displayed anymore.

    Not catching the NoSuchElementException on purpose, so that the
    exception will cause the test to fail.
    """
    self.GetElement(self.ERROR_NOTIFICATION_CLOSE_BUTTON).click()
    # Need to wait for the button's ripple effect to complete.
    WebDriverWait(self.driver, BaseDriver.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located((self.ERROR_NOTIFICATION_CLOSE_BUTTON)))
