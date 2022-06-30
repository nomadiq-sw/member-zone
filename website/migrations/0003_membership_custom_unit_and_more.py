# Generated by Django 4.0.2 on 2022-06-10 05:47

from django.db import migrations, models
import djmoney.models.fields


class Migration(migrations.Migration):
	dependencies = [
		('website', '0002_membership'),
	]

	operations = [
		migrations.AddField(
			model_name='membership',
			name='custom_unit',
			field=models.CharField(choices=[('DAY', 'Days'), ('WEEK', 'Weeks'), ('MONTH', 'Months'), ('YEAR', 'Years')],
								   default='MONTH', max_length=5),
		),
		migrations.AlterField(
			model_name='membership',
			name='cost_currency',
			field=djmoney.models.fields.CurrencyField(
				choices=[('ARS', 'Argentine Peso'), ('AUD', 'Australian Dollar'), ('BDT', 'Bangladeshi Taka'),
						 ('BRL', 'Brazilian Real'), ('GBP', 'British Pound'), ('CAD', 'Canadian Dollar'),
						 ('CLP', 'Chilean Peso'), ('CNY', 'Chinese Yuan'), ('COP', 'Colombian Peso'),
						 ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EGP', 'Egyptian Pound'), ('EUR', 'Euro'),
						 ('HKD', 'Hong Kong Dollar'), ('INR', 'Indian Rupee'), ('IDR', 'Indonesian Rupiah'),
						 ('IRR', 'Iranian Rial'), ('ILS', 'Israeli New Shekel'), ('JPY', 'Japanese Yen'),
						 ('MYR', 'Malaysian Ringgit'), ('MXN', 'Mexican Peso'), ('TWD', 'New Taiwan Dollar'),
						 ('NZD', 'New Zealand Dollar'), ('NGN', 'Nigerian Naira'), ('NOK', 'Norwegian Krone'),
						 ('PKR', 'Pakistani Rupee'), ('PHP', 'Philippine Peso'), ('PLN', 'Polish Zloty'),
						 ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('SAR', 'Saudi Riyal'),
						 ('SGD', 'Singapore Dollar'), ('ZAR', 'South African Rand'), ('KRW', 'South Korean Won'),
						 ('SEK', 'Swedish Krona'), ('CHF', 'Swiss Franc'), ('THB', 'Thai Baht'),
						 ('TRY', 'Turkish Lira'), ('USD', 'US Dollar'), ('AED', 'United Arab Emirates Dirham'),
						 ('VEF', 'Venezuelan Bolívar (2008–2018)'), ('VND', 'Vietnamese Dong')], default='USD',
				editable=False, max_length=3),
		),
		migrations.AlterField(
			model_name='membership',
			name='custom_period',
			field=models.PositiveIntegerField(blank=True, null=True),
		),
	]
