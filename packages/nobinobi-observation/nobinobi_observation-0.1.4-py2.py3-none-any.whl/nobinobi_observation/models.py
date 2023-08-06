# -*- coding: utf-8 -*-
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

from django.db import models
from django.utils.translation import gettext as _
from model_utils import Choices
from model_utils.fields import SplitField
from model_utils.models import TimeStampedModel, StatusModel
from nobinobi_child.models import Child
from nobinobi_staff.models import Staff


class Observation(StatusModel, TimeStampedModel):
    """Model for store observation child"""
    STATUS = Choices(
        ("very_good", "miao.png"),
        ("good", "smile.png"),
        ("bad", "spook.png"),
    )
    staff = models.ForeignKey(
        verbose_name=_("Staff"),
        to=Staff,
        on_delete=models.SET_NULL,
        related_name="observation_staff",
        blank=False,
        null=True,
    )

    child = models.ForeignKey(
        verbose_name=_("Child"),
        to=Child,
        on_delete=models.CASCADE,
    )
    date = models.DateTimeField(_("Date"))
    comment = SplitField(_("Comment"), help_text=_(
        "Looks for the marker &lt;!-- split --&gt; alone on a line "
        "and takes everything before that marker as the excerpt.<br>"
        " If no marker is found in the content, the first two paragraphs "
        "(where paragraphs are blocks of text separated by a blank line) are taken to be the excerpt."))

    class Meta:
        ordering = ('date', 'status',)
        unique_together = ('staff', 'child', 'date')
        verbose_name = _('Observation')
        verbose_name_plural = _('Observations')

    def __str__(self):
        return "{} - {} - {} - {}".format(
            self.child.full_name,
            self.STATUS[self.status],
            self.staff.full_name if self.staff else "",
            self.date
        )
