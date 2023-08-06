# contenda-api-client
A client library for accessing Contenda API

## Usage
First, create a client:

```python
from contenda_api_client import AuthenticatedClient

client = AuthenticatedClient(base_url="https://prod.contenda.io", token="SuperSecretToken")
```

Note: You'll need to exchange a token for your API key first through the identity endpoint. 

Now call your endpoint and use your models:

```python
from contenda_api_client.models import MyDataModel
from contenda_api_client.api.my_tag import get_my_data_model
from contenda_api_client.types import Response

my_data: MyDataModel = get_my_data_model.sync(client=client)
# or if you need more info (e.g. status_code)
response: Response[MyDataModel] = get_my_data_model.sync_detailed(client=client)
```

Or do the same thing with an async version:

```python
from contenda_api_client.models import MyDataModel
from contenda_api_client.api.my_tag import get_my_data_model
from contenda_api_client.types import Response

my_data: MyDataModel = await get_my_data_model.asyncio(client=client)
response: Response[MyDataModel] = await get_my_data_model.asyncio_detailed(client=client)
```

There are more settings on the generated `Client` class which let you control more runtime behavior, check out the docstring on that class for more info.

Things to know:
1. Every path/method combo becomes a Python module with four functions:
    1. `sync`: Blocking request that returns parsed data (if successful) or `None`
    1. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.
    1. `asyncio`: Like `sync` but async instead of blocking
    1. `asyncio_detailed`: Like `sync_detailed` but async instead of blocking

1. All path/query params, and bodies become method arguments.
1. If your endpoint had any tags on it, the first tag will be used as a module name for the function (my_tag above)
1. Any endpoint which did not have a tag will be in `contenda_api_client.api.default`

