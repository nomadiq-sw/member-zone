# Copyright 2022 Owen M. Jones. All rights reserved.
#
# This file is part of MemberZone.
#
# MemberZone is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# MemberZone is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with MemberZone. If not, see <https://www.gnu.org/licenses/>.
# Generated by Django 4.0.2 on 2022-06-10 15:48

from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		('website', '0004_alter_membership_cost_currency'),
	]

	operations = [
		migrations.AlterField(
			model_name='membership',
			name='custom_unit',
			field=models.CharField(blank=True,
								   choices=[('DAY', 'Days'), ('WEEK', 'Weeks'), ('MONTH', 'Months'), ('YEAR', 'Years')],
								   max_length=5, null=True),
		),
	]
