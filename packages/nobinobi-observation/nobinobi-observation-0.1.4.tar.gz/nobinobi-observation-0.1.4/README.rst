=============================
Nobinobi Observation
=============================

.. image:: https://badge.fury.io/py/nobinobi-observation.svg
    :target: https://badge.fury.io/py/nobinobi-observation

.. image:: https://travis-ci.com/prolibre-ch/nobinobi-observation.svg?branch=master
    :target: https://travis-ci.com/prolibre-ch/nobinobi-observation

.. image:: https://codecov.io/gh/prolibre-ch/nobinobi-observation/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/prolibre-ch/nobinobi-observation

Application Observation for Nobinobi

Documentation
-------------

The full documentation is at https://nobinobi-observation.readthedocs.io.

Quickstart
----------

Install Nobinobi Observation::

    pip install nobinobi-observation

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'phonenumber_field',
        'crispy_forms',
        'django_extensions',
        'rest_framework',
        'rest_framework.authtoken',
        'rest_framework_datatables',
        'menu',
        'bootstrap_modal_forms',
        'widget_tweaks',
        'django_select2',
        'bootstrap_datepicker_plus',
        'nobinobi_core',
        'nobinobi_staff',
        'nobinobi_child.apps.NobinobiChildConfig',
        'nobinobi_observation.apps.NobinobiObservationConfig',
        ...
    )

Add Nobinobi Observation's URL patterns:

.. code-block:: python

    from nobinobi_core import urls as nobinobi_core_urls
    from nobinobi_staff import urls as nobinobi_staff_urls
    from nobinobi_child import urls as nobinobi_child_urls
    from nobinobi_observation import urls as nobinobi_observation_urls

    urlpatterns = [
        ...
        path('', include(nobinobi_core_urls)),
        path('', include(nobinobi_staff_urls)),
        path('', include(nobinobi_child_urls)),
        path('', include(nobinobi_observation_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Development commands
---------------------

::

    pip install -r requirements_dev.txt
    invoke -l


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
