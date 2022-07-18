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
from django.db import models
from djmoney.models import fields
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager


# Create your models here.
class SiteUserManager(BaseUserManager):
	"""
	Custom user model manager where email is the unique identifier
	for authentication instead of username.
	"""

	def create_user(self, email, password, **extra_fields):
		"""
		Create and save a User with the given email and password.
		"""
		if not email:
			raise ValueError('The e-mail address must be set')
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, password, **extra_fields):
		"""
		Create and save a SuperUser with the given email and password.
		"""
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_active', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True')
		return self.create_user(email, password, **extra_fields)


class SiteUser(AbstractUser):
	"""
	Custom user model where email is the unique identifier
	for authentication instead of username.
	"""
	username = None
	email = models.EmailField('email', unique=True)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	objects = SiteUserManager()

	def __str__(self):
		return self.email


class Membership(models.Model):
	"""
	Model for membership or subscription
	"""
	MemberPeriod = [
		('WEEKLY', _("Weekly")),
		('MONTHLY', _("Monthly")),
		('ANNUAL', _("Annual")),
		('FIXED', _("Fixed-term")),
		('LIFETIME', _("Lifetime")),
		('CUSTOM', _("Custom"))
	]

	CustomUnit = [
		('DAY', _("Days")),
		('WEEK', _("Weeks")),
		('MONTH', _("Months")),
		('YEAR', _("Years"))
	]

	user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)
	membership_name = models.CharField(max_length=20)
	website_link = models.URLField(blank=True)
	membership_number = models.CharField(blank=True, max_length=30)
	membership_type = models.CharField(choices=MemberPeriod, default='MONTHLY', max_length=8)
	custom_period = models.PositiveIntegerField(blank=True, null=True)  # Required if period = CUSTOM
	custom_unit = models.CharField(choices=CustomUnit, max_length=5, blank=True, null=True)
	renewal_date = models.DateField(blank=True, null=True)  # Required unless period = LIFETIME
	reminder = models.BooleanField(default=False)
	minimum_term = models.DateField(blank=True, null=True)
	free_trial_expiry = models.DateField(blank=True, null=True)
	cost = fields.MoneyField(
		decimal_places=2,
		default=0,
		default_currency='USD',
		max_digits=11
	)
