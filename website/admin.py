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
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SiteUser


class SiteUserAdmin(UserAdmin):
	model = SiteUser
	list_display = ('email', 'is_staff', 'is_active',)
	list_filter = ('email', 'is_staff', 'is_active',)
	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		('Permissions', {'fields': ('is_staff', 'is_active')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
		 ),
	)
	search_fields = ('email',)
	ordering = ('email',)


# Register your models here.
admin.site.register(SiteUser, SiteUserAdmin)
