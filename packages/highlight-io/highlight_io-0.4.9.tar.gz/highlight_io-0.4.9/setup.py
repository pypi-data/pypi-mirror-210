# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['highlight_io', 'highlight_io.integrations']

package_data = \
{'': ['*']}

install_requires = \
['opentelemetry-api>=1.18.0,<2.0.0',
 'opentelemetry-distro[otlp]>=0.39b0,<0.40',
 'opentelemetry-exporter-otlp-proto-http>=1.18.0,<2.0.0',
 'opentelemetry-instrumentation-logging>=0.39b0,<0.40',
 'opentelemetry-instrumentation>=0.39b0,<0.40',
 'opentelemetry-proto>=1.18.0,<2.0.0',
 'opentelemetry-sdk>=1.18.0,<2.0.0']

extras_require = \
{'django': ['django>=4.1.7,<5.0.0'],
 'fastapi': ['fastapi>=0.92.0,<0.93.0', 'uvicorn[standard]>=0.20.0,<0.21.0'],
 'flask': ['blinker>=1.5,<2.0', 'flask>=2.2.2,<3.0.0']}

setup_kwargs = {
    'name': 'highlight-io',
    'version': '0.4.9',
    'description': 'Session replay and error monitoring: stop guessing why bugs happen!',
    'long_description': '# highlight-io Python SDK\n\nThis directory contains the source code for the Highlight Python SDK.\n\n### E2E\n\nThe `e2e` directory contains supported Python frameworks integrated with our SDK for local development and testing.\nDo not use the snippets verbatim as they are configured for local development and will not work in production without changes.\n',
    'author': 'Vadim Korolik',
    'author_email': 'vadim@highlight.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.highlight.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
