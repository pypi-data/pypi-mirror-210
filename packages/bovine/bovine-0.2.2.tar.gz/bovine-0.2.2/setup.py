# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bovine',
 'bovine.activitypub',
 'bovine.activitystreams',
 'bovine.activitystreams.utils',
 'bovine.clients',
 'bovine.crypto',
 'bovine.utils',
 'bovine.utils.msg']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=3.0.0,<4.0.0',
 'aiohttp>=3.8.3,<4.0.0',
 'bleach>=6.0.0,<7.0.0',
 'cryptography>=39.0.0,<40.0.0',
 'multiformats>=0.2.1,<0.3.0',
 'pyld>=2.0.3,<3.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests-cache>=0.9.8,<0.10.0',
 'requests>=2.30.0,<3.0.0',
 'tomli>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'bovine',
    'version': '0.2.2',
    'description': 'Core functionality of bovine needed to build fediverse applications',
    'long_description': '# Bovine\n\nBovine is a basic utility library for the Fediverse. It can be used both to build ActivityPub Client applications and ActivityPub Servers. In addition to [ActivityPub](https://activitypub.rocks/) support, it also provides utilities to deal with [webfinger](https://webfinger.net), nodeinfo, and HTTP Signatures.\n\nThe bovine library can just be installed via pip\n\n```bash\npip install bovine\n```\n\nDocumentation including tutorials is available at [ReadTheDocs](https://bovine.readthedocs.io/en/latest/).\nAn entire working ActivityPub server can be found in the [bovine repository](https://codeberg.org/bovine/bovine/).\n\n## Feedback\n\nIssues about bovine should be filed as an [issue](https://codeberg.org/bovine/bovine/issues).\n\n## Contributing\n\nIf you want to contribute, you can start by working on issues labeled [Good first issue](https://codeberg.org/bovine/bovine/issues?q=&type=all&state=open&labels=110885&milestone=0&assignee=0&poster=0). The tech stack is currently based on asynchronous python, using the following components:\n\n- [aiohttp](https://docs.aiohttp.org/en/stable/index.html) for http requests.\n- [quart](https://quart.palletsprojects.com/en/latest/) as a webserver.\n- [cryptography](https://cryptography.io/en/latest/).\n- [pytest](https://docs.pytest.org/en/7.3.x/) for testing.\n- [ruff](https://pypi.org/project/ruff/) for linting.\n',
    'author': 'Helge',
    'author_email': 'helge.krueger@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://codeberg.org/bovine/bovine',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
