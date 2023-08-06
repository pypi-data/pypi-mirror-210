from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    blog_id: str,
    *,
    client: Client,
    token: str,
) -> Dict[str, Any]:
    url = "{}/api/v2/content/blog/{blog_id}/markdown".format(client.base_url, blog_id=blog_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["token"] = token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "params": params,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[HTTPValidationError, str]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = cast(str, response.json())
        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[HTTPValidationError, str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    blog_id: str,
    *,
    client: Client,
    token: str,
) -> Response[Union[HTTPValidationError, str]]:
    """Get a result blog in markdown format.

     Get a result blog in markdown format.

    NOTE: Image urls expire after 7 days from creation. WIP for a lasting solution.

    Args:
        blog_id (str): ID of the blog in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, str]]
    """

    kwargs = _get_kwargs(
        blog_id=blog_id,
        client=client,
        token=token,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    blog_id: str,
    *,
    client: Client,
    token: str,
) -> Optional[Union[HTTPValidationError, str]]:
    """Get a result blog in markdown format.

     Get a result blog in markdown format.

    NOTE: Image urls expire after 7 days from creation. WIP for a lasting solution.

    Args:
        blog_id (str): ID of the blog in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, str]
    """

    return sync_detailed(
        blog_id=blog_id,
        client=client,
        token=token,
    ).parsed


async def asyncio_detailed(
    blog_id: str,
    *,
    client: Client,
    token: str,
) -> Response[Union[HTTPValidationError, str]]:
    """Get a result blog in markdown format.

     Get a result blog in markdown format.

    NOTE: Image urls expire after 7 days from creation. WIP for a lasting solution.

    Args:
        blog_id (str): ID of the blog in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, str]]
    """

    kwargs = _get_kwargs(
        blog_id=blog_id,
        client=client,
        token=token,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    blog_id: str,
    *,
    client: Client,
    token: str,
) -> Optional[Union[HTTPValidationError, str]]:
    """Get a result blog in markdown format.

     Get a result blog in markdown format.

    NOTE: Image urls expire after 7 days from creation. WIP for a lasting solution.

    Args:
        blog_id (str): ID of the blog in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, str]
    """

    return (
        await asyncio_detailed(
            blog_id=blog_id,
            client=client,
            token=token,
        )
    ).parsed
