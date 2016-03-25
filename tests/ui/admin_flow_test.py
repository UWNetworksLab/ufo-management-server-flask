"""Test admin flows, for now just add."""
import unittest

import flask
import json
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base_test import BaseTest
from login_page import LoginPage
from layout import UfOPageLayout


class AdminFlowTest(BaseTest):

  """Test admin flows."""
  TEST_ADMIN_AS_DICT = {
      'username': 'Test Admin Fake Name 01',
      'password': 'fake admin password that could be anything'
  }

  def setUp(self):
    """Setup for test methods."""
    super(AdminFlowTest, self).setUp()
    super(AdminFlowTest, self).setContext()

  def tearDown(self):
    """Teardown for test methods."""
    self.removeTestAdmin(should_raise_exception=False)
    super(AdminFlowTest, self).tearDown()

  def testAddingAnotherAdminWorks(self):
    """Test that adding another admin works and lets us login as that admin."""
    # Try to login with the uncreated admin to ensure it does not exist.
    LoginPage(self.driver).Login(self.args.server_url,
                                 self.TEST_ADMIN_AS_DICT['username'],
                                 self.TEST_ADMIN_AS_DICT['password'])
    self.driver.get(self.args.server_url + flask.url_for('landing'))

    # Assert that login failed (we're still on the login page).
    login_url = self.args.server_url + flask.url_for('login')
    self.assertEquals(login_url, self.driver.current_url)

    # Login as an existing admin to get access.
    LoginPage(self.driver).Login(self.args.server_url, self.args.username,
                                 self.args.password)
    self.driver.get(self.args.server_url + flask.url_for('landing'))

    # Find the add admin form.
    add_admin_form = self.getAdminFormHelper()
    response_status = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_RESPONSE_STATUS)
    self.assertIsNone(response_status)

    # Add the new admin.
    username_input = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_USERNAME)
    username_real_input = username_input.find_element(By.ID, 'input')
    username_real_input.send_keys(self.TEST_ADMIN_AS_DICT['username'])

    password_input = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_PASSWORD)
    password_real_input = password_input.find_element(By.ID, 'input')
    password_real_input.send_keys(self.TEST_ADMIN_AS_DICT['password'])

    submit_button = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_SUBMIT)
    submit_button.click()

    WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
        EC.invisibility_of_element_located(((
            UfOPageLayout.DROPDOWN_MENU_SPINNER))))

    # Assert that it worked.
    response_status = add_admin_form.find_element(
        *UfOPageLayout.ADD_ADMIN_RESPONSE_STATUS)
    self.assertIsNotNone(response_status)

    # Logout of the existing admin account.
    LoginPage(self.driver).Logout(self.args.server_url)

    # Login as the newly created test admin.
    LoginPage(self.driver).Login(self.args.server_url,
                                 self.TEST_ADMIN_AS_DICT['username'],
                                 self.TEST_ADMIN_AS_DICT['password'])
    self.driver.get(self.args.server_url + flask.url_for('landing'))

    # Assert that login succeeded (we're now on the landing page).
    landing_url = self.args.server_url + flask.url_for('landing')
    self.assertEquals(landing_url, self.driver.current_url)

    # Logout of the test admin account so it can be removed.
    LoginPage(self.driver).Logout(self.args.server_url)

  def getAdminFormHelper(self):
    """Navigates to the admin form on a given page.

    Returns:
      The admin form element once found.
    """
    # Navigate to the add admin flow.
    WebDriverWait(self.driver, BaseTest.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((LoginPage.OPEN_MENU_BUTTON))))
    dropdown_button = self.driver.find_element(*LoginPage.OPEN_MENU_BUTTON)
    dropdown_button.click()

    dropdown_menu = WebDriverWait(self.driver, BaseTest.DEFAULT_TIMEOUT).until(
        EC.visibility_of_element_located(((UfOPageLayout.DROPDOWN_MENU))))
    add_admin_button = dropdown_menu.find_element(
        *UfOPageLayout.ADD_ADMIN_BUTTON)
    add_admin_button.click()

    add_admin_form = WebDriverWait(
        self.driver, BaseTest.DEFAULT_TIMEOUT).until(
            EC.visibility_of_element_located(((UfOPageLayout.ADD_ADMIN_FORM))))
    return add_admin_form

  def removeTestAdmin(self, should_raise_exception=True):
    """Remove a test admin account using a form post (the only way currently).

    Args:
      should_raise_exception: True to raise an exception if the admin is not
                              found.
    """
    # TODO(eholder): Fix this once there is a way in the UI to remove an admin.
    # The method below is based on the admin unit tets.
    # self.driver.get(self.args.server_url + flask.url_for('admin_list'))
    # elem = self.driver.find_element_by_tag_name("pre")
    # json_admins = json.loads(elem.text)['items']
    # test_admin = None
    # for admin in json_admins:
    #   if admin['username'] = self.TEST_ADMIN_AS_DICT['username']:
    #     test_admin = admin
    #     break

    # if test_admin is None:
    #   if should_raise_exception:
    #     raise Exception
    #   else:
    #     return

    # self.driver.get(self.args.server_url + flask.url_for('landing'))
    # xsrf_hidden_input = self.driver.find_element(By.ID, 'globalXsrf')

    # post_data = {
    #   'admin_id': json.dumps(test_admin['id']),
    #   '_xsrf_token': xsrf_hidden_input.get_attribute('value')
    # }
    # response = self.client.post(flask.url_for('delete_admin'), data=post_data)


if __name__ == '__main__':
  unittest.main()
