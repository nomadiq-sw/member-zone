import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from website.models import SiteUser


@pytest.fixture(scope="class")
def setup(request):
	options = Options()
	options.headless = True
	driver = webdriver.Firefox(options=options)
	request.cls.driver = driver
	yield driver
	driver.close()


@pytest.fixture(scope="function")
def new_user():
	email = "juan.gomez@realtalk.com"
	password = "PwdForTest1"
	SiteUser.objects.create_user(email=email, password=password)
