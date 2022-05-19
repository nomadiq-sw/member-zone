import pytest
from django.test import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


# Create your tests here.
@pytest.mark.usefixtures('setup')
class TestUserRegistrationAndLoginForms(LiveServerTestCase):

    def test_registration_form_existing_user(self):
        new_user_email = self.driver.find_element(By.ID, 'id_email')
        new_user_pwd1 = self.driver.find_element(By.ID, 'id_password1')
        new_user_pwd2 = self.driver.find_element(By.ID, 'id_password2')

        register = self.driver.find_element(By.XPATH, ".//input[@value='Register' and @type='submit']")

        new_user_email.send_keys("juan.gomez@realtalk.com")
        new_user_pwd1.send_keys("PwdForTest1")
        new_user_pwd2.send_keys("PwdForTest1")

        register.send_keys(Keys.ENTER)
        delay = 1
        try:
            p_err = WebDriverWait(self.driver, delay).until(ec.presence_of_element_located((By.ID, 'error_1_id_email')))
            self.assertIn("User with this Email already exists", p_err.text)
        except TimeoutException:
            print("Loading took too long!")
