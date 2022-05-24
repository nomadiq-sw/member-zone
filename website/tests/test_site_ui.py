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
        self.new_user_email = self.driver.find_element(By.ID, 'id_email')
        self.new_user_pwd1 = self.driver.find_element(By.ID, 'id_password1')
        self.new_user_pwd2 = self.driver.find_element(By.ID, 'id_password2')
        self.register = self.driver.find_element(By.XPATH, ".//input[@value='Register' and @type='submit']")

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
            p_err = WebDriverWait(self.driver, self.delay)\
                .until(ec.presence_of_element_located((By.ID, 'error_1_id_password2')))
            self.assertIn(string, p_err.text)
        except TimeoutException:
            print("Test case took too long!")
            assert False


@pytest.mark.usefixtures('setup')
class TestUserRegistrationFormSuccess(LiveServerTestCase):

    def setUp(self):
        self.driver.get(self.live_server_url+'/memberships/login')
        self.new_user_email = self.driver.find_element(By.ID, 'id_email')
        self.new_user_pwd1 = self.driver.find_element(By.ID, 'id_password1')
        self.new_user_pwd2 = self.driver.find_element(By.ID, 'id_password2')
        self.register = self.driver.find_element(By.XPATH, ".//input[@value='Register' and @type='submit']")

    def test_new_user_success(self):

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


@pytest.mark.usefixtures('setup')
class TestUserLoginFormErrors(LiveServerTestCase):

    def setUp(self):
        self.delay = 2
        self.driver.get(self.live_server_url+'/memberships/login')
        self.user_email = self.driver.find_element(By.ID, 'id_username')
        self.user_pwd = self.driver.find_element(By.ID, 'id_password')
        self.login = self.driver.find_element(By.XPATH, ".//input[@value='Login' and @type='submit']")

    def test_login_invalid_email(self):
        self.user_email.send_keys("juan.gomez@realtalk.com")
        self.user_pwd.send_keys("PwdForTest1")
        self.login.send_keys(Keys.ENTER)

        self.check_string_in_login_err("Incorrect email or password. Please try again.")

    def test_login_right_email_wrong_pwd(self):
        SiteUser.objects.create_user(email="juan.gomez@realtalk.com", password="PwdForTest1")
        self.user_email.send_keys("juan.gomez@realtalk.com")
        self.user_pwd.send_keys("PwdForTest2")
        self.login.send_keys(Keys.ENTER)

        self.check_string_in_login_err("Incorrect email or password. Please try again.")

    def test_login_inactive_user(self):
        SiteUser.objects.create_user(email="juan.gomez@realtalk.com", password="PwdForTest1", is_active=False)
        self.user_email.send_keys("juan.gomez@realtalk.com")
        self.user_pwd.send_keys("PwdForTest1")
        self.login.send_keys(Keys.ENTER)

        self.check_string_in_login_err("Incorrect email or password. Please try again.")

    def check_string_in_login_err(self, string):
        try:
            alert_xpath = "//form[@action='/memberships/login']/div[1]/div/ul/li[1]"
            login_err = WebDriverWait(self.driver, self.delay) \
                .until(ec.presence_of_element_located((By.XPATH, alert_xpath)))
            self.assertIn(string, login_err.text)
        except TimeoutException:
            print("Test case took too long!")
            assert False


@pytest.mark.usefixtures('setup')
class TestUserLoginFormSuccess(LiveServerTestCase):

    def setUp(self):
        self.driver.get(self.live_server_url+'/memberships/login')
        self.user_email = self.driver.find_element(By.ID, 'id_username')
        self.user_pwd = self.driver.find_element(By.ID, 'id_password')
        self.login = self.driver.find_element(By.XPATH, ".//input[@value='Login' and @type='submit']")

    def test_user_login_success(self):
        SiteUser.objects.create_user(email="juan.gomez@realtalk.com", password="PwdForTest1")
        self.user_email.send_keys("juan.gomez@realtalk.com")
        self.user_pwd.send_keys("PwdForTest1")
        self.login.send_keys(Keys.ENTER)

        try:
            WebDriverWait(self.driver, 2)\
                .until(ec.url_matches(self.live_server_url+'/memberships/my-memberships'))
        except TimeoutException:
            print("User login failed!")
        finally:
            self.assertURLEqual(self.driver.current_url, self.live_server_url+'/memberships/my-memberships/')
