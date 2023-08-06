from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.get_rss_feed_parsed_api_v2_blog_rss_feed_parsed_get_response_get_rss_feed_parsed_api_v2_blog_rss_feed_parsed_get import (
    GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    rss_link: str,
    token_limit: Union[Unset, None, int] = 7000,
    token: str,
) -> Dict[str, Any]:
    url = "{}/api/v2/blog/rss-feed-parsed".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["rss_link"] = rss_link

    params["token_limit"] = token_limit

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


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[
    Union[
        GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet, HTTPValidationError
    ]
]:
    if response.status_code == HTTPStatus.OK:
        response_200 = (
            GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet.from_dict(
                response.json()
            )
        )

        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[
    Union[
        GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet, HTTPValidationError
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    rss_link: str,
    token_limit: Union[Unset, None, int] = 7000,
    token: str,
) -> Response[
    Union[
        GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet, HTTPValidationError
    ]
]:
    """Parse RSS feed.

     EXPERIMENTAL: RSS feed parser for listicle.fun web app.

    Args:
        rss_link (str):
        token_limit (Union[Unset, None, int]):  Default: 7000.
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        client=client,
        rss_link=rss_link,
        token_limit=token_limit,
        token=token,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    rss_link: str,
    token_limit: Union[Unset, None, int] = 7000,
    token: str,
) -> Optional[
    Union[
        GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet, HTTPValidationError
    ]
]:
    """Parse RSS feed.

     EXPERIMENTAL: RSS feed parser for listicle.fun web app.

    Args:
        rss_link (str):
        token_limit (Union[Unset, None, int]):  Default: 7000.
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        rss_link=rss_link,
        token_limit=token_limit,
        token=token,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    rss_link: str,
    token_limit: Union[Unset, None, int] = 7000,
    token: str,
) -> Response[
    Union[
        GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet, HTTPValidationError
    ]
]:
    """Parse RSS feed.

     EXPERIMENTAL: RSS feed parser for listicle.fun web app.

    Args:
        rss_link (str):
        token_limit (Union[Unset, None, int]):  Default: 7000.
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        client=client,
        rss_link=rss_link,
        token_limit=token_limit,
        token=token,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    rss_link: str,
    token_limit: Union[Unset, None, int] = 7000,
    token: str,
) -> Optional[
    Union[
        GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet, HTTPValidationError
    ]
]:
    """Parse RSS feed.

     EXPERIMENTAL: RSS feed parser for listicle.fun web app.

    Args:
        rss_link (str):
        token_limit (Union[Unset, None, int]):  Default: 7000.
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetRssFeedParsedApiV2BlogRssFeedParsedGetResponseGetRssFeedParsedApiV2BlogRssFeedParsedGet, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            rss_link=rss_link,
            token_limit=token_limit,
            token=token,
        )
    ).parsed
