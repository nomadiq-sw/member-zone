# Copyright 2022 Owen M. Jones. All rights reserved.
#
# This file is part of MemberZone.
#
# MemberZone is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License 
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# MemberZone is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with MemberZone. If not, see <https://www.gnu.org/licenses/>.
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
def new_user(request):
	email = "juan.gomez@realtalk.com"
	password = "PwdForTest1"
	user = SiteUser.objects.create_user(email=email, password=password)
	request.cls.user = user
	yield user
	user.delete()


@pytest.fixture(scope="function")
def cookie(request, new_user, client):
	client.force_login(new_user)
	cookie = client.cookies['sessionid']
	request.cls.cookie = cookie
	yield cookie
	client.logout()
