import pytest
from selenium import webdriver


@pytest.fixture(scope="class")
def setup(request):
    driver = webdriver.Firefox()
    driver.get("http://127.0.0.1:8000/memberships/login")
    driver.maximize_window()
    request.cls.driver = driver

    yield driver
    driver.close()
