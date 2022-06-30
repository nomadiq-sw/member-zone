# Generated by Django 4.0.2 on 2022-06-10 06:02

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):
	dependencies = [
		('website', '0003_membership_custom_unit_and_more'),
	]

	operations = [
		migrations.AlterField(
			model_name='membership',
			name='cost_currency',
			field=djmoney.models.fields.CurrencyField(
				choices=[('AED', 'AED'), ('ARS', 'ARS'), ('AUD', 'AUD'), ('BDT', 'BDT'), ('BRL', 'BRL'), ('CAD', 'CAD'),
						 ('CHF', 'CHF'), ('CLP', 'CLP'), ('CNY', 'CNY'), ('COP', 'COP'), ('CZK', 'CZK'), ('DKK', 'DKK'),
						 ('EGP', 'EGP'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('HKD', 'HKD'), ('IDR', 'IDR'), ('ILS', 'ILS'),
						 ('INR', 'INR'), ('IRR', 'IRR'), ('JPY', 'JPY'), ('KRW', 'KRW'), ('MXN', 'MXN'), ('MYR', 'MYR'),
						 ('NGN', 'NGN'), ('NOK', 'NOK'), ('NZD', 'NZD'), ('PHP', 'PHP'), ('PKR', 'PKR'), ('PLN', 'PLN'),
						 ('RON', 'RON'), ('RUB', 'RUB'), ('SAR', 'SAR'), ('SEK', 'SEK'), ('SGD', 'SGD'), ('THB', 'THB'),
						 ('TRY', 'TRY'), ('TWD', 'TWD'), ('USD', 'USD'), ('VEF', 'VEF'), ('VND', 'VND'),
						 ('ZAR', 'ZAR')], default='USD', editable=False, max_length=3),
		),
	]
