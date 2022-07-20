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
from celery import shared_task
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from django.db import transaction
from django.template.loader import get_template
from django.core.mail import send_mail, BadHeaderError
from smtplib import SMTPException

import config.settings
from .models import Membership, SiteUser
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# In the following functions we declare overlapping reminder periods so that users get
# two reminders of each expiry date with appropriate advance warning in each case:
def day_reminders():
	qsd1 = Membership.objects.filter(membership_type__in=('WEEKLY', 'MONTHLY'))
	qsd2 = Membership.objects.filter(
		membership_type__in='CUSTOM',
		custom_unit='DAY',
		custom_period__lte=90
	)
	qsd3 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='WEEK',
		custom_period__lte=12
	)
	qsd4 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='MONTH',
		custom_period__lte=3
	)
	return (qsd1.union(qsd2, qsd3, qsd4)) \
		.intersection(Membership.objects.filter(reminder=True, renewal_date=datetime.today()+timedelta(days=1)))


def week_reminders():
	qsw1 = Membership.objects.filter(membership_type__in=('MONTHLY', 'ANNUAL', 'FIXED'))
	qsw2 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='DAY',
		custom_period__range=(30, 90)
	)
	qsw3 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='WEEK',
		custom_period__range=(4, 12)
	)
	qsw4 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='MONTH',
		custom_period__lte=3
	)

	return (qsw1.union(qsw2, qsw3, qsw4)) \
		.intersection(Membership.objects.filter(reminder=True, renewal_date=datetime.today()+timedelta(days=7)))


def month_reminders():
	qsm1 = Membership.objects.filter(membership_type__in=('ANNUAL', 'FIXED'))
	qsm2 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='DAY',
		custom_period__gt=90
	)
	qsm3 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='WEEK',
		custom_period__gt=12
	)
	qsm4 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='MONTH',
		custom_period__gt=3
	)
	qsm5 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='YEAR'
	)

	return (qsm1.union(qsm2, qsm3, qsm4, qsm5)) \
		.intersection(Membership.objects.filter(reminder=True, renewal_date=datetime.today()+timedelta(days=30)))


# We also send free trial expiry reminders 7 days before and 1 day before in each case:
def free_trial_expiry_reminders():
	return Membership.objects.filter(
		reminder=True,
		free_trial_expiry__in=(datetime.today()+timedelta(days=1), datetime.today()+timedelta(days=7))
	)


@shared_task(name="reminder_emails")
def reminder_emails():
	users = SiteUser.objects.all()
	for user in users:
		renewal_mail = html_renewal_email(user)
		free_trial_mail = html_free_trial_expiry_email(user)
		if renewal_mail:
			try:
				subject = "A reminder from MemberZone: memberships coming up for renewal"
				send_mail(subject, renewal_mail, f"noreply@{config.settings.ROOT_DOMAIN}", [user.email])
			except BadHeaderError as e:
				logger.error(f"Exception {e} while sending renewal reminder to {user.email}")
			except SMTPException as e:
				logger.error(f"Exception {e} while sending renewal reminder to {user.email}")
		if free_trial_mail:
			try:
				subject = "A reminder from MemberZone: free trials expiring soon"
				send_mail(subject, free_trial_mail, f"noreply@{config.settings.ROOT_DOMAIN}", [user.email])
			except BadHeaderError as e:
				logger.error(f"Exception {e} while sending free trial expiry reminder to {user.email}")
			except SMTPException as e:
				logger.error(f"Exception {e} while sending free trial expiry reminder to {user.email}")


def html_renewal_email(user):
	user_reminders = (day_reminders().union(week_reminders(), month_reminders()))\
		.intersection(Membership.objects.filter(user=user)).order_by('renewal_date')
	if user_reminders.count() != 0:
		html_temp = get_template('reminders/membership_renewal_reminder_email.html')
		c = {
			'protocol': config.settings.PROTOCOL,
			'domain': config.settings.DOMAIN,
			'items': user_reminders.all(),
		}
		return html_temp.render(c)
	return None


def html_free_trial_expiry_email(user):
	user_reminders = free_trial_expiry_reminders()\
		.intersection(Membership.objects.filter(user=user)).order_by('free_trial_expiry')
	if user_reminders.count() != 0:
		html_temp = get_template('reminders/free_trial_expiry_reminder_email.html')
		c = {
			'protocol': config.settings.PROTOCOL,
			'domain': config.settings.DOMAIN,
			'items': user_reminders.all(),
		}
		return html_temp.render(c)
	return None


@shared_task(name="renewal_updates")
def renewal_updates():
	today = datetime.today()
	mems = Membership.objects.filter(membership_type__in=('WEEKLY', 'MONTHLY', 'ANNUAL', 'CUSTOM'), renewal_date=today)
	with transaction.atomic():
		for mem in mems:
			if mem.membership_type == 'CUSTOM' and mem.custom_unit == 'DAY':
				mem.renewal_date += timedelta(days=mem.custom_period)
			elif mem.membership_type == 'WEEKLY' or (mem.membership_type == 'CUSTOM' and mem.custom_unit == 'WEEK'):
				n = mem.custom_period or 1
				mem.renewal_date += timedelta(weeks=n)
			elif mem.membership_type == 'MONTHLY' or (mem.membership_type == 'CUSTOM' and mem.custom_unit == 'MONTH'):
				n = mem.custom_period or 1
				mem.renewal_date += relativedelta(months=+n)
			elif mem.membership_type == 'ANNUAL' or (mem.membership_type == 'CUSTOM' and mem.custom_unit == 'YEAR'):
				n = mem.custom_period or 1
				mem.renewal_date += relativedelta(years=+n)
			mem.save()
