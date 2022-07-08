from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(name="print_msg_main")
def print_message(message, *args, **kwargs):
	logger.info(f"Celery is working!! Message is '{message}'")


@shared_task(name="print_time")
def print_time():
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S")
	logger.info(f"Current time is {current_time}")
