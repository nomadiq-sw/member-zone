import pytest
import re
from django.test import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail
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
            self.assertURLEqual(self.driver.current_url, self.live_server_url+'/memberships/my-memberships')


@pytest.mark.usefixtures('setup')
class TestUserLoginFormErrors(LiveServerTestCase):

    def setUp(self):
        self.delay = 2
        self.driver.get(self.live_server_url+'/memberships/login')
        self.user_email = self.driver.find_element(By.ID, 'id_username')
        self.user_pwd = self.driver.find_element(By.ID, 'id_password')
        self.login = self.driver.find_element(By.XPATH, ".//input[@value='Log in' and @type='submit']")

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
        self.login = self.driver.find_element(By.XPATH, ".//input[@value='Log in' and @type='submit']")

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
            self.assertURLEqual(self.driver.current_url, self.live_server_url+'/memberships/my-memberships')


@pytest.mark.usefixtures('setup')
class TestPasswordResetForm(LiveServerTestCase):

    def setUp(self):
        self.driver.get(self.live_server_url+'/password-reset')
        self.reset_email = self.driver.find_element(By.ID, 'id_email')
        self.reset_button = self.driver.find_element(By.XPATH, ".//input[@value='Reset password' and @type='submit']")

    def test_reset_password_valid_email(self):
        SiteUser.objects.create_user(email="juan.gomez@realtalk.com", password="PwdForTest1")
        self.reset_email.send_keys("juan.gomez@realtalk.com")
        self.reset_button.send_keys(Keys.ENTER)

        try:
            WebDriverWait(self.driver, 2)\
                .until(ec.url_matches(self.live_server_url+'/password-reset/done'))
        except TimeoutException:
            print("Password reset failed!")
        finally:
            self.assertURLEqual(self.driver.current_url, self.live_server_url+'/password-reset/done')
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, "Password Reset Requested")
            email_content = mail.outbox[0].body
            user = SiteUser.objects.get(email="juan.gomez@realtalk.com")
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            uid_token_regex = r"password-reset\/"+re.escape(uid)+r"\/([A-Za-z0-9:\-]+)"
            match = re.search(uid_token_regex, email_content)
            assert match, "UID and token not found in email"
            token = match.group(1)

            self.driver.get(self.live_server_url+'/password-reset/'+uid+'/'+token)
            try:
                WebDriverWait(self.driver, 2) \
                    .until(ec.url_matches(self.live_server_url+'/password-reset/'+uid+'/set-password'))
            except TimeoutException:
                print("Redirect to password reset page failed!")
            finally:
                self.assertURLEqual(self.driver.current_url,
                                    self.live_server_url+'/password-reset/'+uid+'/set-password')
                new_pwd1 = self.driver.find_element(By.ID, 'id_new_password1')
                new_pwd2 = self.driver.find_element(By.ID, 'id_new_password2')
                set_pwd = self.driver.find_element(By.XPATH, ".//input[@value='Change password' and @type='submit']")
                new_pwd1.send_keys("PwdForTest2")
                new_pwd2.send_keys("PwdForTest2")
                set_pwd.send_keys(Keys.ENTER)
                try:
                    WebDriverWait(self.driver, 2) \
                        .until(ec.url_matches(self.live_server_url+'/password-reset/complete'))
                except TimeoutException:
                    print("Updating password failed!")
                finally:
                    self.assertURLEqual(self.driver.current_url,
                                        self.live_server_url+'/password-reset/complete')
                    user = SiteUser.objects.get(email="juan.gomez@realtalk.com")
                    assert user.check_password("PwdForTest2")

    def test_reset_password_invalid_email(self):
        self.reset_email.send_keys("juan.gomez@realtalk.com")
        self.reset_button.send_keys(Keys.ENTER)

        try:
            WebDriverWait(self.driver, 2)\
                .until(ec.url_matches(self.live_server_url+'/password-reset/invalid'))
        except TimeoutException:
            print("Password reset invalidation failed!")
        finally:
            self.assertURLEqual(self.driver.current_url, self.live_server_url+'/password-reset/invalid')
