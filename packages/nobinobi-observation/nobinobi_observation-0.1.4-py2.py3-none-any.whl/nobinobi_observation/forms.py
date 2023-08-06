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

from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from bootstrap_modal_forms.forms import BSModalModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django import forms
from django.utils.translation import gettext as _
from django_select2.forms import ModelSelect2Widget
from nobinobi_child.models import Child
from nobinobi_core.widgets import InlineRadiosImage
from nobinobi_staff.models import Staff

from nobinobi_observation.models import Observation


class ObservationCreateForm(forms.ModelForm):
    child = forms.ModelChoiceField(
        label=_("Child"), queryset=Child.objects.filter(status=Child.STATUS.in_progress),
        widget=ModelSelect2Widget(
            model=Child,
            queryset=Child.objects.filter(status=Child.STATUS.in_progress),
            search_fields=['first_name__icontains', 'last_name__icontains']
        )
    )
    staff = forms.ModelChoiceField(
        label=_("Staff"),
        queryset=Staff.objects.filter(status=Staff.STATUS.active),
        widget=ModelSelect2Widget(
            model=Staff,
            queryset=Staff.objects.filter(status=Staff.STATUS.active),
            search_fields=['first_name__icontains', 'last_name__icontains']
        )
    )

    # date = forms.SplitDateTimeField(label=_("Date"), widget=widgets.AdminSplitDateTime(),)

    class Meta:
        model = Observation
        fields = ('status', "child", "date", "staff", "comment")
        widgets = {
            "date": DateTimePickerInput(
                options={
                    "locale": "fr",
                    "format": "DD/MM/YYYY HH:MM"
                }),
            "comment": forms.Textarea
        }

    def __init__(self, request=None, *args, **kwargs):
        super(ObservationCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # self.helper.form_show_labels = False
        self.helper.form_tag = True
        self.helper.layout = Layout(
            # Div(
            Field("child", wrapper_class="col-sm-12 col-md-6"),
            Field("staff", wrapper_class="col-sm-12 col-md-6"),
            # css_class="row"
            # ),
            # Div(
            Field("date", wrapper_class="col-sm-12 col-md-6"),
            InlineRadiosImage("status", wrapper_class="col-sm-12 col-md-6"),
            # css_class="row"
            # ),
            Field("comment"),
        )
        self.helper.add_input(Submit("submit", _("Create")))


class ObservationUpdateForm(BSModalModelForm):
    staff = forms.ModelChoiceField(
        label=_("Staff"),
        queryset=Staff.objects.filter(status=Staff.STATUS.active),
        widget=ModelSelect2Widget(
            model=Staff,
            queryset=Staff.objects.filter(status=Staff.STATUS.active),
            search_fields=['first_name__icontains', 'last_name__icontains']
        )
    )

    class Meta:
        model = Observation
        fields = ('status', "date", "staff", "comment")
        widgets = {
            "date": DateTimePickerInput(
                options={
                    "locale": "fr",
                    "format": "DD/MM/YYYY HH:MM"
                })
        }


class ObservationChoiceForm(forms.Form):
    child = forms.ModelChoiceField(
        label=_("Child"),
        queryset=Child.objects.filter(status=Child.STATUS.in_progress),
        widget=ModelSelect2Widget(
            model=Child,
            queryset=Child.objects.filter(status=Child.STATUS.in_progress),
            search_fields=['first_name__icontains', 'last_name__icontains']
        )
    )

    def __init__(self, request=None, *args, **kwargs):
        super(ObservationChoiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_show_labels = False
        self.helper.form_tag = True
        # self.helper.layout = Layout(        )
        self.helper.add_input(Submit("submit", _("Submit")))
