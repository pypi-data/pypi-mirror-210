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

from bootstrap_modal_forms.generic import BSModalReadView, BSModalDeleteView, BSModalUpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import (
    CreateView,
    ListView,
    FormView, TemplateView)
from nobinobi_child.models import Child
from rest_framework import viewsets

from nobinobi_observation.forms import ObservationCreateForm, ObservationChoiceForm, ObservationUpdateForm
from nobinobi_observation.models import Observation
from nobinobi_observation.serializers import ObservationSerializer


class ObservationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ObservationSerializer

    def get_queryset(self):
        return Observation.objects.filter(child_id=self.kwargs.get("child_pk")).order_by("-date")


class ObservationCreateView(LoginRequiredMixin, CreateView):
    model = Observation
    form_class = ObservationCreateForm

    def form_valid(self, form):
        pk = form.cleaned_data['child'].pk
        self.object = form.save()
        return HttpResponseRedirect(reverse("nobinobi_observation:Observation_detail_list", kwargs={"pk": pk}))


class ObservationDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Observation
    template_name = 'nobinobi_observation/observation_confirm_delete.html'
    success_message = _("The observation was successfully deleted.")

    def get_success_url(self):
        return reverse("nobinobi_observation:Observation_detail_list", kwargs={"pk": self.object.child.pk})


class ObservationDetailView(LoginRequiredMixin, BSModalReadView):
    model = Observation
    template_name = 'nobinobi_observation/observation_detail.html'


class ObservationUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Observation
    form_class = ObservationUpdateForm
    template_name = 'nobinobi_observation/observation_update.html'
    success_message = _("The observation was successfully updated.")

    def get_success_url(self):
        return reverse("nobinobi_observation:Observation_detail_list", kwargs={"pk": self.object.child.pk})


class ObservationListView(LoginRequiredMixin, ListView):
    model = Observation


class ObservationDetailListView(LoginRequiredMixin, TemplateView):
    template_name = "nobinobi_observation/observation_detail_list.html"

    def get_context_data(self, **kwargs):
        context = super(ObservationDetailListView, self).get_context_data(**kwargs)
        context['title'] = _("List of observations")
        context['child'] = get_object_or_404(Child, pk=kwargs["pk"])
        context['observation_list'] = Observation.objects.filter(child=kwargs["pk"])
        return context


class ObservationChoiceView(LoginRequiredMixin, FormView):
    form_class = ObservationChoiceForm
    template_name = "nobinobi_observation/observation_choice.html"

    def form_valid(self, form):
        pk = form.cleaned_data['child'].pk
        return HttpResponseRedirect(reverse("nobinobi_observation:Observation_detail_list", kwargs={"pk": pk}))
