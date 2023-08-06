# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['contenda_api_client',
 'contenda_api_client.api',
 'contenda_api_client.api.content_and_results',
 'contenda_api_client.api.experimental',
 'contenda_api_client.api.identity',
 'contenda_api_client.api.jobs',
 'contenda_api_client.api.media',
 'contenda_api_client.api.utility',
 'contenda_api_client.models']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.3.0', 'httpx>=0.15.4,<0.25.0', 'python-dateutil>=2.8.0,<3.0.0']

setup_kwargs = {
    'name': 'contenda-api-client',
    'version': '0.1.1',
    'description': 'A client library for accessing Contenda API',
    'long_description': '# contenda-api-client\nA client library for accessing Contenda API\n\n## Usage\nFirst, create a client:\n\n```python\nfrom contenda_api_client import AuthenticatedClient\n\nclient = AuthenticatedClient(base_url="https://prod.contenda.io", token="SuperSecretToken")\n```\n\nNote: You\'ll need to exchange a token for your API key first through the identity endpoint. \n\nNow call your endpoint and use your models:\n\n```python\nfrom contenda_api_client.models import MyDataModel\nfrom contenda_api_client.api.my_tag import get_my_data_model\nfrom contenda_api_client.types import Response\n\nmy_data: MyDataModel = get_my_data_model.sync(client=client)\n# or if you need more info (e.g. status_code)\nresponse: Response[MyDataModel] = get_my_data_model.sync_detailed(client=client)\n```\n\nOr do the same thing with an async version:\n\n```python\nfrom contenda_api_client.models import MyDataModel\nfrom contenda_api_client.api.my_tag import get_my_data_model\nfrom contenda_api_client.types import Response\n\nmy_data: MyDataModel = await get_my_data_model.asyncio(client=client)\nresponse: Response[MyDataModel] = await get_my_data_model.asyncio_detailed(client=client)\n```\n\nThere are more settings on the generated `Client` class which let you control more runtime behavior, check out the docstring on that class for more info.\n\nThings to know:\n1. Every path/method combo becomes a Python module with four functions:\n    1. `sync`: Blocking request that returns parsed data (if successful) or `None`\n    1. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.\n    1. `asyncio`: Like `sync` but async instead of blocking\n    1. `asyncio_detailed`: Like `sync_detailed` but async instead of blocking\n\n1. All path/query params, and bodies become method arguments.\n1. If your endpoint had any tags on it, the first tag will be used as a module name for the function (my_tag above)\n1. Any endpoint which did not have a tag will be in `contenda_api_client.api.default`\n\n',
    'author': 'Lilly Chen',
    'author_email': 'lilly@contenda.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
