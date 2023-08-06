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

from django.urls import reverse
from django.utils.translation import gettext as _
from menu import Menu, MenuItem
from .utils import has_view_observation

Menu.add_item(
    "main",
    MenuItem(
        title=_("Observations"),
        url="/observation/",
        icon="fa fa-eye",
        children=[
            MenuItem(
                title=_("Journal of observations"),
                url=reverse("nobinobi_observation:Observation_choice"),
                icon="fas fa-list"),
            MenuItem(
                title=_("Add Observation"),
                url=reverse("nobinobi_observation:Observation_create"),
                icon="fas fa-plus"),
        ],
        check=lambda request: has_view_observation(request)
    )
)

# Menu.add_item("main", MenuItem("Staff Only",
#                                reverse("reports.views.staff"),
#                                check=lambda request: request.user.is_staff))
#
# Menu.add_item("main", MenuItem("Superuser Only",
#                                reverse("reports.views.superuser"),
#                                check=lambda request: request.user.is_superuser))
