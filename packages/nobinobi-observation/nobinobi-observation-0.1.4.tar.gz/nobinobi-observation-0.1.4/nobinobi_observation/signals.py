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

import logging
from sys import stdout

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from nobinobi_observation.models import Observation

GROUP_NAME = getattr(settings, "GROUP_NAME_USERS", "Users")
ADMIN_GROUP_NAME = getattr(settings, "GROUP_NAME_ADMIN", "Admin")


def create_group_nobinobi_observation(sender, **kwargs):
    observation_type = ContentType.objects.get_for_model(Observation)
    group, created = Group.objects.get_or_create(name=('%s' % GROUP_NAME))
    if created:
        logging.info('%s Group created' % GROUP_NAME)
        stdout.write(_("Groups {} created successfully.").format(group))
        # Code to add permission to group ???
    permissions = [
        (observation_type, "add_observation"),
        # (observation_type, "change_observation"),
        # (observation_type, "delete_observation"),
        (observation_type, "view_observation"),
    ]
    # Now what - Say I want to add 'Can add project' permission to new_group?
    permission_list = []
    for content_type, perm in permissions:
        permission_list.append(
            Permission.objects.get(content_type=content_type, codename=perm))

    for permission in permission_list:
        group.permissions.add(permission)
        stdout.write(_("Permission {} added to {} successfully.\n").format(permission, group))


def create_group_admin_nobinobi_observation(sender, **kwargs):
    observation_type = ContentType.objects.get_for_model(Observation)
    group, created = Group.objects.get_or_create(name=('%s' % ADMIN_GROUP_NAME))
    if created:
        logging.info('%s Group created' % ADMIN_GROUP_NAME)
        stdout.write(_("Groups {} created successfully.").format(group))
        # Code to add permission to group ???
    permissions = [
        (observation_type, "add_observation"),
        (observation_type, "change_observation"),
        (observation_type, "delete_observation"),
        (observation_type, "view_observation"),

    ]  # Now what - Say I want to add 'Can add project' permission to new_group?
    permission_list = []
    for content_type, perm in permissions:
        permission_list.append(
            Permission.objects.get(content_type=content_type, codename=perm))

    for permission in permission_list:
        group.permissions.add(permission)
        stdout.write(_("Permission {} added to {} successfully.\n").format(permission, group))
