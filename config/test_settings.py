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
"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent

NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5+7dtxe3%%+rlvoejx2_*&no354o+a7ve^p9v*ozb7*gokty!v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

PROTOCOL = 'http'

DOMAIN = "127.0.0.1:8000"
ROOT_DOMAIN = "member-zone.net"

APPEND_SLASH = False

INTERNAL_IPS = [
	"127.0.0.1",
]
# Application definition

INSTALLED_APPS = [
	'website',
	'tailwind',
	'theme',
	'captcha',
	'django_htmx',
	'widget_tweaks',
	'crispy_forms',
	'crispy_tailwind',
	'django_browser_reload',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'djmoney',
	'django_celery_beat',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django_htmx.middleware.HtmxMiddleware',
	'django_browser_reload.middleware.BrowserReloadMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'config.wsgi.application'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = 'user@email.com'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': BASE_DIR / 'db.sqlite3',
	}
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
AUTH_USER_MODEL = 'website.SiteUser'

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
		'OPTIONS': {
			'max_similarity': 0.6,  # Default of 0.7 is too weak, allows password very similar to email in some cases
		}
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

LOGIN_URL = 'login'

LOGOUT_REDIRECT_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CURRENCIES = ('EUR', 'GBP', 'CHF', 'NOK', 'SEK', 'DKK', 'CZK', 'PLN', 'RON',
			  'TRY', 'RUB',
			  'USD', 'CAD', 'MXN', 'BRL', 'ARS', 'CLP', 'COP', 'VEF',
			  'AUD', 'NZD',
			  'INR', 'JPY', 'CNY', 'KRW', 'HKD', 'MYR', 'IDR', 'PHP', 'SGD', 'TWD', 'THB', 'VND', 'PKR', 'BDT',
			  'SAR', 'AED', 'ILS', 'IRR',
			  'ZAR', 'EGP', 'NGN')  # List based on 50 largest economies according to worlddata.info

CURRENCY_CHOICES = [('EUR', 'EUR'), ('GBP', 'GBP'), ('CHF', 'CHF'), ('NOK', 'NOK'), ('SEK', 'SEK'), ('DKK', 'DKK'),
					('CZK', 'CZK'), ('PLN', 'PLN'), ('RON', 'RON'),
					('TRY', 'TRY'), ('RUB', 'RUB'),
					('USD', 'USD'), ('CAD', 'CAD'), ('MXN', 'MXN'), ('BRL', 'BRL'), ('ARS', 'ARS'), ('CLP', 'CLP'),
					('COP', 'COP'), ('VEF', 'VEF'),
					('AUD', 'AUD'), ('NZD', 'NZD'),
					('INR', 'INR'), ('JPY', 'JPY'), ('CNY', 'CNY'), ('KRW', 'KRW'), ('HKD', 'HKD'), ('MYR', 'MYR'),
					('IDR', 'IDR'), ('PHP', 'PHP'), ('SGD', 'SGD'),
					('TWD', 'TWD'), ('THB', 'THB'), ('VND', 'VND'), ('PKR', 'PKR'), ('BDT', 'BDT'),
					('SAR', 'SAR'), ('AED', 'AED'), ('ILS', 'ILS'), ('IRR', 'IRR'),
					('ZAR', 'ZAR'), ('EGP', 'EGP'), ('NGN', 'NGN')]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

CRISPY_ALLOWED_TEMPLATE_PACKS = ('tailwind',)
CRISPY_TEMPLATE_PACK = 'tailwind'

TAILWIND_APP_NAME = 'theme'

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery configuration

CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
