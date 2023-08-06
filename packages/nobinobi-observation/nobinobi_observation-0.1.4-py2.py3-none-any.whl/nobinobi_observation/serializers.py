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

from nobinobi_staff.serializers import StaffSerializer
from rest_framework import serializers

from nobinobi_observation.models import Observation


class ObservationSerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)

    class Meta:
        model = Observation
        fields = ["id", "staff", "date", "comment", "_comment_excerpt", "status"]
        # depth = 2
        datatables_always_serialize = ("id", "staff", "date", "comment", "status")

    def to_representation(self, instance):
        representation = super(ObservationSerializer, self).to_representation(instance)
        representation['status'] = instance.STATUS[instance.status]

        return representation
