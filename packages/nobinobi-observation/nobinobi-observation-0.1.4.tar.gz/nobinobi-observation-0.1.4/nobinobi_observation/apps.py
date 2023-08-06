# -*- coding: utf-8
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

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class NobinobiObservationConfig(AppConfig):
    name = 'nobinobi_observation'

    def ready(self):
        from nobinobi_observation.signals import create_group_nobinobi_observation, \
            create_group_admin_nobinobi_observation
        post_migrate.connect(create_group_nobinobi_observation, sender=self)
        post_migrate.connect(create_group_admin_nobinobi_observation, sender=self)
