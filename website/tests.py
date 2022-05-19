from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Create your tests here.
class UserRegistrationFormTest(LiveServerTestCase):

    def testRegistrationFormExistingUser(self):
        driver = webdriver.Firefox()
        driver.get("http://127.0.0.1:8000/memberships/login")

        new_user_email = driver.find_element(By.ID, 'id_email')
        new_user_pwd1 = driver.find_element(By.ID, 'id_password1')
        new_user_pwd2 = driver.find_element(By.ID, 'id_password2')

        register = driver.find_element(By.XPATH, ".//input[@value='Register' and @type='submit']")

        new_user_email.send_keys("juan.gomez@realtalk.com")
        new_user_pwd1.send_keys("PwdForTest1")
        new_user_pwd2.send_keys("PwdForTest1")

        register.send_keys(Keys.ENTER)
        delay = 1
        try:
            p_err = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'error_1_id_email')))
            self.assertIn("User with this Email already exists.", p_err.text)
        except TimeoutException:
            print("Loading took too long!")
        except NoSuchElementException:
            print("Element 'error_1_id_email' not found!")
