import moneyed
import pytest
import re
from django.test import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as ec
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail
from datetime import date, timedelta
from time import sleep
from decimal import Decimal
from website.models import SiteUser, Membership


# Create your tests here.
@pytest.mark.usefixtures('setup')
class TestUserRegistrationFormErrors(LiveServerTestCase):

	def setUp(self):
		self.driver.get(self.live_server_url + '/memberships/login')
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
			e_err = WebDriverWait(self.driver, self.delay) \
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
			p_err = WebDriverWait(self.driver, self.delay) \
				.until(ec.presence_of_element_located((By.ID, 'error_1_id_password2')))
			self.assertIn(string, p_err.text)
		except TimeoutException:
			print("Test case took too long!")
			assert False


@pytest.mark.usefixtures('setup')
class TestUserRegistrationFormSuccess(LiveServerTestCase):

	def setUp(self):
		self.driver.get(self.live_server_url + '/memberships/login')
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
			WebDriverWait(self.driver, 2) \
				.until(ec.url_matches(self.live_server_url + '/memberships/my-memberships'))
		except TimeoutException:
			print("New user creation failed!")
		finally:
			self.assertURLEqual(self.driver.current_url, self.live_server_url + '/memberships/my-memberships')
			self.assertEqual(len(mail.outbox), 1)
			self.assertEqual(mail.outbox[0].subject, "Welcome to MemberZone")


@pytest.mark.usefixtures('setup')
class TestUserLoginFormErrors(LiveServerTestCase):

	def setUp(self):
		self.delay = 2
		self.driver.get(self.live_server_url + '/memberships/login')
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


@pytest.mark.usefixtures('setup', 'new_user')
class TestUserLoginFormSuccess(LiveServerTestCase):

	def setUp(self):
		self.driver.get(self.live_server_url + '/memberships/login')
		self.user_email = self.driver.find_element(By.ID, 'id_username')
		self.user_pwd = self.driver.find_element(By.ID, 'id_password')
		self.login = self.driver.find_element(By.XPATH, ".//input[@value='Log in' and @type='submit']")

	def test_user_login_success(self):
		self.user_email.send_keys("juan.gomez@realtalk.com")
		self.user_pwd.send_keys("PwdForTest1")
		self.login.send_keys(Keys.ENTER)
		try:
			WebDriverWait(self.driver, 2) \
				.until(ec.url_matches(self.live_server_url + '/memberships/my-memberships'))
		except TimeoutException:
			print("User login failed!")
		finally:
			self.assertURLEqual(self.driver.current_url, self.live_server_url + '/memberships/my-memberships')

		logout_button = self.driver.find_element(By.ID, 'login-button')
		logout_button.send_keys(Keys.ENTER)
		try:
			WebDriverWait(self.driver, 2) \
				.until(ec.url_matches(self.live_server_url + '/index'))
		except TimeoutException:
			print("User logout failed!")
		finally:
			self.assertURLEqual(self.driver.current_url, self.live_server_url + '/')
			login_button = self.driver.find_element(By.ID, 'login-button')
			self.assertIn("Log in", login_button.text)


@pytest.mark.usefixtures('setup', 'new_user')
class TestPasswordResetForm(LiveServerTestCase):

	def setUp(self):
		self.driver.get(self.live_server_url + '/password-reset')
		self.reset_email = self.driver.find_element(By.ID, 'id_email')
		self.reset_button = self.driver.find_element(By.XPATH, ".//input[@value='Reset password' and @type='submit']")

	def test_reset_password_valid_email(self):
		self.reset_email.send_keys("juan.gomez@realtalk.com")
		self.reset_button.send_keys(Keys.ENTER)

		try:
			WebDriverWait(self.driver, 2) \
				.until(ec.url_matches(self.live_server_url + '/password-reset/done'))
		except TimeoutException:
			print("Password reset failed!")
		finally:
			self.assertURLEqual(self.driver.current_url, self.live_server_url + '/password-reset/done')
			self.assertEqual(len(mail.outbox), 1)
			self.assertEqual(mail.outbox[0].subject, "Password reset requested")
			email_content = mail.outbox[0].body
			user = SiteUser.objects.get(email="juan.gomez@realtalk.com")
			uid = urlsafe_base64_encode(force_bytes(user.pk))
			uid_token_regex = r"password-reset\/" + re.escape(uid) + r"\/([A-Za-z0-9:\-]+)"
			match = re.search(uid_token_regex, email_content)
			assert match, "UID and token not found in email"
			token = match.group(1)

			self.driver.get(self.live_server_url + '/password-reset/' + uid + '/' + token)
			try:
				WebDriverWait(self.driver, 2) \
					.until(ec.url_matches(self.live_server_url + '/password-reset/' + uid + '/set-password'))
			except TimeoutException:
				print("Redirect to password reset page failed!")
			finally:
				self.assertURLEqual(self.driver.current_url,
									self.live_server_url + '/password-reset/' + uid + '/set-password')
				new_pwd1 = self.driver.find_element(By.ID, 'id_new_password1')
				new_pwd2 = self.driver.find_element(By.ID, 'id_new_password2')
				set_pwd = self.driver.find_element(By.XPATH, ".//input[@value='Change password' and @type='submit']")
				new_pwd1.send_keys("PwdForTest2")
				new_pwd2.send_keys("PwdForTest2")
				set_pwd.send_keys(Keys.ENTER)
				try:
					WebDriverWait(self.driver, 2) \
						.until(ec.url_matches(self.live_server_url + '/password-reset/complete'))
				except TimeoutException:
					print("Updating password failed!")
				finally:
					self.assertURLEqual(self.driver.current_url,
										self.live_server_url + '/password-reset/complete')
					user = SiteUser.objects.get(email="juan.gomez@realtalk.com")
					assert user.check_password("PwdForTest2")

	def test_reset_password_invalid_email(self):
		self.reset_email.send_keys("pablo.gomez@realtalk.com")
		self.reset_button.send_keys(Keys.ENTER)

		try:
			WebDriverWait(self.driver, 2) \
				.until(ec.url_matches(self.live_server_url + '/password-reset/invalid'))
		except TimeoutException:
			print("Password reset invalidation failed!")
		finally:
			self.assertURLEqual(self.driver.current_url, self.live_server_url + '/password-reset/invalid')


@pytest.mark.usefixtures('setup', 'new_user', 'cookie')
class TestNewMembershipForm(LiveServerTestCase):

	def setUp(self):
		self.driver.get(self.live_server_url)
		self.driver.add_cookie({'name': 'sessionid', 'value': self.cookie.value, 'secure': False, 'path': '/'})
		self.driver.get(self.live_server_url + '/memberships/my-memberships')

		self.name = self.driver.find_element(By.ID, 'id_membership_name')
		self.m_type = Select(self.driver.find_element(By.NAME, 'membership_type'))
		self.m_url = self.driver.find_element(By.ID, 'id_website_link')
		self.m_num = self.driver.find_element(By.ID, 'id_membership_number')
		self.renewal = self.driver.find_element(By.ID, 'id_renewal_date')
		self.custom_p = self.driver.find_element(By.ID, 'id_custom_period')
		self.custom_u = Select(self.driver.find_element(By.NAME, 'custom_unit'))
		self.cost_val = self.driver.find_element(By.ID, 'id_cost_0')
		self.cost_cur = Select(self.driver.find_element(By.ID, 'id_cost_1'))
		self.submit = self.driver.find_element(By.XPATH, ".//button[@type='submit']")

	def test_new_membership_missing_dates(self):
		self.name.send_keys("Toto")
		self.m_type.select_by_visible_text("Custom")
		self.submit.send_keys(Keys.ENTER)
		self.check_string_in_form_err("You have selected a custom membership but have not set a renewal date")
		self.check_string_in_form_err("You have selected a custom membership but have not set a valid custom period")

	def test_new_membership_past_date(self):
		self.name.send_keys("Toto")
		self.m_type.select_by_visible_text("Monthly")
		self.renewal.send_keys("2022-01-01")
		self.submit.send_keys(Keys.ENTER)
		self.check_string_in_form_err("The renewal date cannot be in the past")

	def test_new_membership_success(self):
		renew_date = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
		self.name.send_keys("Toto")
		self.m_type.select_by_visible_text("Custom")
		self.m_url.send_keys("http://www.toto.org")
		self.m_num.send_keys("1234567890")
		self.renewal.send_keys(renew_date)
		self.custom_p.send_keys("6")
		self.custom_u.select_by_visible_text("Weeks")
		self.cost_val.send_keys(Keys.DELETE + "19.99")
		self.cost_cur.select_by_visible_text("GBP")
		self.submit.send_keys(Keys.ENTER)

		try:
			WebDriverWait(self.driver, 2) \
				.until(ec.visibility_of_element_located((By.ID, 'alert-success')))
		except TimeoutException:
			print("Adding new membership failed!")
			assert False
		objects = Membership.objects.filter(membership_name="Toto")
		assert objects.count() == 1
		membership = objects[0]
		assert membership.user == self.user
		assert membership.membership_name == "Toto"
		assert membership.membership_type == "CUSTOM"
		assert membership.website_link == "http://www.toto.org"
		assert membership.membership_number == "1234567890"
		assert membership.renewal_date.strftime("%Y-%m-%d") == renew_date
		assert membership.custom_period == 6
		assert membership.custom_unit == "WEEK"
		assert membership.reminder is False
		assert membership.cost.amount == Decimal('19.99')
		assert membership.cost.currency == moneyed.GBP

		try:
			WebDriverWait(self.driver, 1) \
				.until(ec.text_to_be_present_in_element((By.ID, 'membership-table-body'), "Toto"))
		except TimeoutException:
			print("New membership details did not appear in table!")
		finally:
			t_body = self.driver.find_element(By.ID, 'membership-table-body')
			self.assertIn("Toto", t_body.text)
			self.assertIn("Custom", t_body.text)
			self.assertIn("£19.99", t_body.text)

	def check_string_in_form_err(self, string):
		try:
			error = WebDriverWait(self.driver, 1) \
				.until(ec.presence_of_element_located((By.XPATH, ".//div[@class='alert mb-4']")))
			self.assertIn(string, error.text)
		except TimeoutException:
			print("Non-field errors not found in form!")
			assert False


@pytest.mark.usefixtures('setup', 'new_user', 'cookie')
class TestMembershipEditAndDelete(LiveServerTestCase):

	def setUp(self):
		renew_date = (date.today() + timedelta(days=3))
		self.membership = Membership.objects.create(
			user=self.user,
			membership_name="Toto",
			membership_type="MONTHLY",
			renewal_date=renew_date,
			reminder=True,
			cost=moneyed.Money(Decimal(19.99), moneyed.USD)
		)
		self.membership.save()
		assert Membership.objects.count() == 1

		self.driver.get(self.live_server_url)
		self.driver.add_cookie({'name': 'sessionid', 'value': self.cookie.value, 'secure': False, 'path': '/'})
		self.driver.get(self.live_server_url + '/memberships/my-memberships')

	def test_toggle_reminders(self):
		mems = Membership.objects.filter(membership_name=self.membership.membership_name)
		cb = self.driver.find_element(By.XPATH, ".//input[@type='checkbox']")
		sleep(1)  # Necessary in this case to stop test being flaky
		cb.click()
		assert mems[0].reminder is not self.membership.reminder
		cb.click()
		assert mems[0].reminder is self.membership.reminder

	def test_delete_membership(self):
		a_del = self.driver.find_element(By.XPATH, ".//a[contains(text(), 'Delete')]")
		self.driver.execute_script("window.confirm = function(){return true;}")  # Needed for headless tests
		a_del.click()
		assert Membership.objects.count() == 0
		self.driver.refresh()
		t_body = self.driver.find_element(By.ID, 'membership-table-body')
		self.assertIn("Nothing to see here", t_body.text)

	def test_edit_membership_details(self):
		a_edit = self.driver.find_element(By.XPATH, ".//a[contains(text(), 'Edit')]")
		WebDriverWait(self.driver, 1).until(ec.element_to_be_clickable(a_edit))
		a_edit.click()
		try:
			WebDriverWait(self.driver, 2) \
				.until(ec.text_to_be_present_in_element_value(
					(By.ID, 'id_membership_name'),
					self.membership.membership_name
				))
		except TimeoutException:
			print("Membership details did not load!")
			assert False
		name = self.driver.find_element(By.ID, 'id_membership_name')
		m_type = Select(self.driver.find_element(By.NAME, 'membership_type'))
		m_num = self.driver.find_element(By.ID, 'id_membership_number')
		renewal = self.driver.find_element(By.ID, 'id_renewal_date')
		cost_val = self.driver.find_element(By.ID, 'id_cost_0')
		cost_cur = Select(self.driver.find_element(By.ID, 'id_cost_1'))
		submit = self.driver.find_element(By.XPATH, ".//button[@type='submit']")

		self.assertEqual(self.membership.membership_name, name.get_attribute('value'))
		self.assertEqual(self.membership.membership_type, m_type.first_selected_option.text.upper())
		self.assertEqual(self.membership.renewal_date.strftime("%Y-%m-%d"), renewal.get_attribute('value'))
		self.assertAlmostEqual(self.membership.cost.amount, float(cost_val.get_attribute('value')), places=2)
		self.assertEqual(str(self.membership.cost.currency), cost_cur.first_selected_option.text)

		m_type.select_by_visible_text("Annual")
		m_num.send_keys("1234567890")
		cost_val.clear()
		cost_val.send_keys("14.99")
		submit.send_keys(Keys.ENTER)

		try:
			WebDriverWait(self.driver, 2) \
				.until(ec.visibility_of_element_located((By.ID, 'alert-success')))
		except TimeoutException:
			print("Updating membership failed!")
			assert False
		mems = Membership.objects.filter(membership_name=self.membership.membership_name)
		assert mems.count() == 1
		assert mems[0].membership_type == "ANNUAL"
		assert mems[0].membership_number == "1234567890"
		assert mems[0].cost.amount == Decimal('14.99')

		t_body = self.driver.find_element(By.ID, 'membership-table-body')
		self.assertIn("Annual", t_body.text)
		self.assertIn("$14.99", t_body.text)
