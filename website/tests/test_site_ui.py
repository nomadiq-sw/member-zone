import pytest
from django.test import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from website.models import SiteUser


# Create your tests here.
@pytest.mark.usefixtures('setup')
class TestUserRegistrationFormErrors(LiveServerTestCase):

    def setUp(self):
        self.driver.get(self.live_server_url+'/memberships/login')
        self.delay = 1
        try:
            WebDriverWait(self.driver, self.delay) \
                .until(ec.presence_of_element_located((By.ID, 'id_email')))
            self.new_user_email = self.driver.find_element(By.ID, 'id_email')
            WebDriverWait(self.driver, self.delay) \
                .until(ec.presence_of_element_located((By.ID, 'id_password1')))
            self.new_user_pwd1 = self.driver.find_element(By.ID, 'id_password1')
            WebDriverWait(self.driver, self.delay) \
                .until(ec.presence_of_element_located((By.ID, 'id_password2')))
            self.new_user_pwd2 = self.driver.find_element(By.ID, 'id_password2')
            WebDriverWait(self.driver, self.delay) \
                .until(ec.presence_of_element_located((By.XPATH, ".//input[@value='Register' and @type='submit']")))
            self.register = self.driver.find_element(By.XPATH, ".//input[@value='Register' and @type='submit']")
        except TimeoutException:
            print("Loading took too long!")
            assert False

    def test_registration_existing_user(self):
        SiteUser.objects.create_user(email="juan.gomez@realtalk.com", password="PwdForTest1")
        self.new_user_email.send_keys("juan.gomez@realtalk.com")
        self.new_user_pwd1.send_keys("PwdForTest1")
        self.new_user_pwd2.send_keys("PwdForTest1")
        self.register.send_keys(Keys.ENTER)
        try:
            e_err = WebDriverWait(self.driver, self.delay)\
                .until(ec.presence_of_element_located((By.ID, 'error_1_id_email')))
            self.assertIn("User with this Email already exists.", e_err.text)
        except TimeoutException:
            print("Error took too long!")
            assert False

    def test_registration_pwd_similar_email(self):
        self.new_user_email.send_keys("pedro.gomez@realtalk.com")
        self.new_user_pwd1.send_keys("pedro.gomez")
        self.new_user_pwd2.send_keys("pedro.gomez")
        self.register.send_keys(Keys.ENTER)

        self.check_string_in_pwd_err("The password is too similar to the email.")

    def test_registration_pwd_too_short(self):
        self.new_user_email.send_keys("pedro.gomez@realtalk.com")
        self.new_user_pwd1.send_keys("nvjdia0")
        self.new_user_pwd2.send_keys("nvjdia0")
        self.register.send_keys(Keys.ENTER)

        self.check_string_in_pwd_err("This password is too short.")

    def test_registration_pwd_too_common(self):
        self.new_user_email.send_keys("pedro.gomez@realtalk.com")
        # See https://gist.github.com/roycewilliams/281ce539915a947a23db17137d91aeb7
        self.new_user_pwd1.send_keys("target123")
        self.new_user_pwd2.send_keys("target123")
        self.register.send_keys(Keys.ENTER)

        self.check_string_in_pwd_err("This password is too common.")

    def test_registration_pwd_numeric(self):
        self.new_user_email.send_keys("pedro.gomez@realtalk.com")
        self.new_user_pwd1.send_keys("86743909")
        self.new_user_pwd2.send_keys("86743909")
        self.register.send_keys(Keys.ENTER)

        self.check_string_in_pwd_err("This password is entirely numeric.")

    def test_registration_mismatched_passwords(self):
        self.new_user_email.send_keys("pedro.gomez@realtalk.com")
        self.new_user_pwd1.send_keys("86743909dbq")
        self.new_user_pwd2.send_keys("86743909dba")
        self.register.send_keys(Keys.ENTER)

        self.check_string_in_pwd_err("The two password fields didn’t match.")

    def check_string_in_pwd_err(self, string):
        try:
            if not self.driver.find_elements(By.ID, 'error_1_id_password2'):
                WebDriverWait(self.driver, self.delay)\
                    .until(ec.presence_of_element_located((By.ID, 'error_1_id_password2')))
            else:
                curr = self.driver.find_element(By.ID, 'error_1_id_password2').text
                WebDriverWait(self.driver, self.delay)\
                    .until(lambda d: d.find_element(By.ID, 'error_1_id_password2').text != curr)
            p_err = self.driver.find_element(By.ID, 'error_1_id_password2').text
            self.assertIn(string, p_err)
        except TimeoutException:
            print("Test case took too long!")
            assert False


@pytest.mark.usefixtures('setup')
class TestRegistrationFormSuccess(LiveServerTestCase):

    def setUp(self):
        self.driver.get(self.live_server_url+'/memberships/login')

    def test_new_user_success(self):
        self.new_user_email = self.driver.find_element(By.ID, 'id_email')
        self.new_user_pwd1 = self.driver.find_element(By.ID, 'id_password1')
        self.new_user_pwd2 = self.driver.find_element(By.ID, 'id_password2')
        self.register = self.driver.find_element(By.XPATH, ".//input[@value='Register' and @type='submit']")

        self.new_user_email.send_keys("pedro.gomez@realtalk.com")
        self.new_user_pwd1.send_keys("86743909dba")
        self.new_user_pwd2.send_keys("86743909dba")
        self.register.send_keys(Keys.ENTER)

        try:
            WebDriverWait(self.driver, 2)\
                .until(ec.url_matches(self.live_server_url+'/memberships/my-memberships'))
        except TimeoutException:
            print("New user creation failed!")
        finally:
            self.assertURLEqual(self.driver.current_url, self.live_server_url+'/memberships/my-memberships/')
