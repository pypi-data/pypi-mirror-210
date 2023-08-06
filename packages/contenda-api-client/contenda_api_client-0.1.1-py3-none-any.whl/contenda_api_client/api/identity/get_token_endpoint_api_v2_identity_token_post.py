from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.generate_access_token import GenerateAccessToken
from ...models.get_token_endpoint_api_v2_identity_token_post_response_get_token_endpoint_api_v2_identity_token_post import (
    GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: GenerateAccessToken,
) -> Dict[str, Any]:
    url = "{}/api/v2/identity/token".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "json": json_json_body,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[
    Union[GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost, HTTPValidationError]
]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost.from_dict(
            response.json()
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
    Union[GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost, HTTPValidationError]
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
    json_body: GenerateAccessToken,
) -> Response[
    Union[GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost, HTTPValidationError]
]:
    """Get Token Endpoint

     Generate a JWT Access token with a user e-mail and an API key.

    **Request body:**
    - `email` (`string`): user's e-mail address
    - `api_key` (`string`): user's API key

    Args:
        json_body (GenerateAccessToken): Generate access token model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    json_body: GenerateAccessToken,
) -> Optional[
    Union[GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost, HTTPValidationError]
]:
    """Get Token Endpoint

     Generate a JWT Access token with a user e-mail and an API key.

    **Request body:**
    - `email` (`string`): user's e-mail address
    - `api_key` (`string`): user's API key

    Args:
        json_body (GenerateAccessToken): Generate access token model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: GenerateAccessToken,
) -> Response[
    Union[GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost, HTTPValidationError]
]:
    """Get Token Endpoint

     Generate a JWT Access token with a user e-mail and an API key.

    **Request body:**
    - `email` (`string`): user's e-mail address
    - `api_key` (`string`): user's API key

    Args:
        json_body (GenerateAccessToken): Generate access token model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    json_body: GenerateAccessToken,
) -> Optional[
    Union[GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost, HTTPValidationError]
]:
    """Get Token Endpoint

     Generate a JWT Access token with a user e-mail and an API key.

    **Request body:**
    - `email` (`string`): user's e-mail address
    - `api_key` (`string`): user's API key

    Args:
        json_body (GenerateAccessToken): Generate access token model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetTokenEndpointApiV2IdentityTokenPostResponseGetTokenEndpointApiV2IdentityTokenPost, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
