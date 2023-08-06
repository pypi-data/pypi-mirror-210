# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_batteries']

package_data = \
{'': ['*']}

install_requires = \
['django>=4.1.7,<5.0.0', 'djangorestframework>=3.14.0,<4.0.0']

setup_kwargs = {
    'name': 'django-batteries',
    'version': '0.0.2',
    'description': 'Set of most common utils for django/drf projects',
    'long_description': "# Django-batteries\n\nThis package contains useful utilities for django/drf project\n\n## Models\n\nContains set of abstract models to enforce DRY principle for most common use cases\n\n### `django_batteries.models.TimeStampedModel`\n\n- `created`\n- `modified`\n\n### `django_batteries.models.TimeFramedModel`\n\n- `start`\n- `end`\n\n  For time bound entities\n\n### `django_batteries.models.DescriptionModel`\n\n- `description`\n\n### `django_batteries.models.TitleModel`\n\n- `title`\n\n### `django_batteries.models.TitleDescriptionModel`\n\n- `title`\n- `description`\n\n## Fields\n\n### Monitor field\n\nA DateTimeField that monitors another field on the same model and sets itself to the current date/time whenever the monitored field\nchanges.\nuse it like this in your models:\nclass MyMode(models.Model):\n\n    title = models.Charfield(max_length=50)\n    title_changed = MonitorField(_('title changed'), monitor='title')\n\n## Mixins\n\n### `django_batteries.mixins.ListSerializerMixin`\n\nAllow you to specify `list_serializer_class` that will be used only in list action\n\n## Paginators\n\n### django_batteries.paginators.ResultSetPagination\n\nPaginator with `page_size` as query parameter for setting page size\n\n### django_batteries.paginators.SingleResultPaginator\n\nCustom paginator class that returns not paginated(detail result) if qs result have only 1 item\n\n## Utils\n\n### django_batteries.utils.qs_admin_or_author\n\nReturn all objects if user is staff, otherwise return objects owned by user\n",
    'author': 'Oleksandr Korol',
    'author_email': 'zibertua@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
