# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['novu', 'novu.api', 'novu.dto', 'novu.enums']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.2,<3.0.0']

setup_kwargs = {
    'name': 'novu',
    'version': '1.3.0a1',
    'description': 'This project aims to provide a wrapper for the Novu API.',
    'long_description': '# Python Novu SDK\n\n[![PyPI](https://img.shields.io/pypi/v/novu?color=blue)](https://pypi.org/project/novu/)\n![Tests Status](https://github.com/novuhq/novu-python/actions/workflows/.github/workflows/tests.yml/badge.svg)\n[![codecov](https://codecov.io/gh/novuhq/novu-python/branch/main/graph/badge.svg?token=RON7F8QTZX)](https://codecov.io/gh/novuhq/novu-python)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/novu)\n![PyPI - License](https://img.shields.io/pypi/l/novu)\n[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)\n\n---\n\nThe [Python Novu](https://novu.co) SDK and package provides a fluent and expressive interface for interacting with [Novu\'s API](https://api.novu.co/api) and managing notifications.\n\n## Install\n\nTo install this package\n\n```shell\n# Via pip\npip install novu\n\n# Via poetry\npoetry add novu\n```\n\n## Quick start\n\nThis package is a wrapper of all the resources offered by Novu, we will just start by triggering an event on Novu.\n\nTo do this, you will need to:\n\n1. Create your first notification template and keep in mind the identifier to trigger the template: https://docs.novu.co/overview/quick-start#create-a-notification-template\n2. Retrieve your API key from the Novu dashboard directly in the settings section: https://web.novu.co/settings\n3. Write code to trigger your first event:\n\n```python\nfrom novu.api import EventApi\n\nevent_api = EventApi("https://api.novu.co/api/", "<NOVU_API_TOKEN>")\nevent_api.trigger(\n    name="<YOUR_TEMPLATE_NAME>",\n    recipients="<YOUR_SUBSCRIBER_ID>",\n    payload={},  # Your Novu payload goes here\n)\n```\n\nThis will trigger a notification to the subscribers.\n\n## Development\n\n```bash\n# install deps\npoetry install\n\n# pre-commit\npoetry run pre-commit install --install-hook\npoetry run pre-commit install --install-hooks --hook-type commit-msg\n```\n',
    'author': 'oscar.marie-taillefer',
    'author_email': 'oscar.marie-taillefer@spikeelabs.fr',
    'maintainer': 'oscar.marie-taillefer',
    'maintainer_email': 'oscar.marie-taillefer@spikeelabs.fr',
    'url': 'https://novu-python.readthedocs.io/en/latest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
