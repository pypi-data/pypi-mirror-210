#  Copyright (c) 2021 <Florian Alu - alu@prolibre.com - https://www.prolibre.com>
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from django.contrib import admin

from nobinobi_observation.models import Observation


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    """
        Admin View for Observation
    """
    # readonly_fields = ('_comment_excerpt',)
    fields = ('child', 'staff', 'date', 'status', 'comment')
    list_display = ('child', "staff", "date", "status")
    list_filter = ('child', "staff", "date", "status")
    search_fields = ('child__last_name', "child__first_name", "staff__first_name", "staff__last_name", "comment")
