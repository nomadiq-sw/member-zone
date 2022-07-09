from celery import shared_task
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from django.db import transaction
from .models import Membership, SiteUser
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def day_reminders():
	qsd1 = Membership.objects.filter(membership_type__in=('WEEKLY', 'FIXED'))
	qsd2 = Membership.objects.filter(
		membership_type__in='CUSTOM',
		custom_unit='DAY',
		custom_period__range=(2, 14)
	)
	qsd3 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='WEEK',
		custom_period__lte=2
	)
	return (qsd1.union(qsd2, qsd3)) \
		.intersection(Membership.objects.filter(reminder=True, renewal_date=datetime.today()+timedelta(days=1)))


def week_reminders():
	qsw1 = Membership.objects.filter(membership_type__in=('MONTHLY', 'FIXED'))
	qsw2 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='DAY',
		custom_period__range=(15, 90)
	)
	qsw3 = Membership.objects.filter(
		membership_type='CUSTOM',
		custom_unit='WEEK',
		custom_period__range=(3, 12)
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


def free_trial_expiry_reminders():
	return Membership.objects.filter(
		reminder=True,
		free_trial_expiry__in=(datetime.today()+timedelta(days=1), datetime.today()+timedelta(days=7))
	)


@shared_task(name="reminder_emails")
def reminder_emails():
	today = datetime.today()
	users = SiteUser.objects.all()
	pass


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
