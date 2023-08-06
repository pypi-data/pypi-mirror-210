from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from ... import errors
from ...client import Client
from ...models.health_health_get_response_health_health_get import HealthHealthGetResponseHealthHealthGet
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/health".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[HealthHealthGetResponseHealthHealthGet]:
    if response.status_code == HTTPStatus.OK:
        response_200 = HealthHealthGetResponseHealthHealthGet.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[HealthHealthGetResponseHealthHealthGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
) -> Response[HealthHealthGetResponseHealthHealthGet]:
    """Test service health.

     Test service health, helps validate if the service is running.

    If there are HTTP 4XX or HTTP 5XX errors for this request, please contact support.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HealthHealthGetResponseHealthHealthGet]
    """

    kwargs = _get_kwargs(
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
) -> Optional[HealthHealthGetResponseHealthHealthGet]:
    """Test service health.

     Test service health, helps validate if the service is running.

    If there are HTTP 4XX or HTTP 5XX errors for this request, please contact support.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HealthHealthGetResponseHealthHealthGet
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
) -> Response[HealthHealthGetResponseHealthHealthGet]:
    """Test service health.

     Test service health, helps validate if the service is running.

    If there are HTTP 4XX or HTTP 5XX errors for this request, please contact support.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HealthHealthGetResponseHealthHealthGet]
    """

    kwargs = _get_kwargs(
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
) -> Optional[HealthHealthGetResponseHealthHealthGet]:
    """Test service health.

     Test service health, helps validate if the service is running.

    If there are HTTP 4XX or HTTP 5XX errors for this request, please contact support.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HealthHealthGetResponseHealthHealthGet
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
