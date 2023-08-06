# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beeline',
 'beeline.middleware',
 'beeline.middleware.awslambda',
 'beeline.middleware.bottle',
 'beeline.middleware.django',
 'beeline.middleware.flask',
 'beeline.middleware.werkzeug',
 'beeline.patch',
 'beeline.propagation']

package_data = \
{'': ['*']}

install_requires = \
['libhoney>=2.3.0,<3.0.0', 'wrapt>=1.12.1,<2.0.0']

entry_points = \
{'console_scripts': ['tests = beeline.test_suite:run_tests']}

setup_kwargs = {
    'name': 'honeycomb-beeline',
    'version': '3.5.2',
    'description': 'Honeycomb library for easy instrumentation',
    'long_description': '# Honeycomb Beeline for Python\n\n[![OSS Lifecycle](https://img.shields.io/osslifecycle/honeycombio/beeline-python?color=success)](https://github.com/honeycombio/home/blob/main/honeycomb-oss-lifecycle-and-practices.md)\n[![Build Status](https://circleci.com/gh/honeycombio/beeline-python.svg?style=svg)](https://app.circleci.com/pipelines/github/honeycombio/beeline-python)\n\n**Note**: Honeycomb embraces OpenTelemetry as the effective way to instrument applications. For any new observability efforts, we recommend [instrumenting with OpenTelemetry](https://docs.honeycomb.io/getting-data-in/opentelemetry/python-distro/).\n\nThis package makes it easy to instrument your Python web application to send useful events to [Honeycomb](https://honeycomb.io), a service for debugging your software in production.\n\n- [Usage and Examples](https://docs.honeycomb.io/getting-data-in/beelines/beeline-python/)\n- [API Reference](https://honeycombio.github.io/beeline-python/)\n\n## Compatible with\n\nCurrently, supports Django (>3.2), Flask, Bottle, and Tornado.\n\nCompatible with Python >3.7.\n\n## Updating to 3.3.0\n\nVersion 3.3.0 added support for Environment & Services, which changes sending behavior based on API Key.\n\nIf you are using the [FileTransmission](https://github.com/honeycombio/libhoney-py/blob/main/libhoney/transmission.py#L448) method and setting a false API key - and still working in Classic mode - you must update the key to be 32 characters in length to keep the same behavior.\n\n## Contributions\n\nFeatures, bug fixes and other changes to `beeline-python` are gladly accepted.\n\nIf you add a new test module, be sure and update `beeline.test_suite` to pick up the new tests.\n\nAll contributions will be released under the Apache License 2.0.\n',
    'author': 'Honeycomb.io',
    'author_email': 'feedback@honeycomb.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/honeycombio/beeline-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
