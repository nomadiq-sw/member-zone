import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


@pytest.fixture(scope="class")
def setup(request):
	options = Options()
	options.headless = True
	driver = webdriver.Firefox(options=options)
	request.cls.driver = driver
	yield driver
	driver.close()
