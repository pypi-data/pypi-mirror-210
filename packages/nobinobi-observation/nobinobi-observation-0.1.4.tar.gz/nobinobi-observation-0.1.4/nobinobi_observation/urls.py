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

from django.urls import path, include

from nobinobi_observation import views

app_name = 'nobinobi_observation'
urlpatterns = [
    path(
        'api/observation/<uuid:child_pk>/',
        views.ObservationViewSet.as_view({'get': 'list'}),
        name='api-observation'
    ),
    path("observation/", include([
        path("observation/", include([
            path("",
                 view=views.ObservationListView.as_view(),
                 name='Observation_list',
                 ),
            path("~create/",
                 view=views.ObservationCreateView.as_view(),
                 name='Observation_create',
                 ),
            path("~choice/",
                 view=views.ObservationChoiceView.as_view(),
                 name='Observation_choice',
                 ),
            path("child/<uuid:pk>/",
                 view=views.ObservationDetailListView.as_view(),
                 name='Observation_detail_list',
                 ),
            path("<int:pk>/", include([
                path("",
                     view=views.ObservationDetailView.as_view(),
                     name='Observation_detail', ),
                path("~delete/",
                     view=views.ObservationDeleteView.as_view(),
                     name='Observation_delete', ),
                path("~update/",
                     view=views.ObservationUpdateView.as_view(),
                     name='Observation_update',
                     ),
            ])),
        ]))
    ]))
]
