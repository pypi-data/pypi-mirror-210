from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.get_job_api_v2_jobs_status_job_id_get_response_get_job_api_v2_jobs_status_job_id_get import (
    GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    job_id: str,
    *,
    client: Client,
    token: str,
) -> Dict[str, Any]:
    url = "{}/api/v2/jobs/status/{job_id}".format(client.base_url, job_id=job_id)

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


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet, HTTPValidationError]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet.from_dict(response.json())

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
) -> Response[Union[GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_id: str,
    *,
    client: Client,
    token: str,
) -> Response[Union[GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet, HTTPValidationError]]:
    """Get job status.

     Get the status of a job.

    Args:
        job_id (str): ID of the job, e.g. `uncertainty-rk-family-am-reflections-jo`
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        client=client,
        token=token,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_id: str,
    *,
    client: Client,
    token: str,
) -> Optional[Union[GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet, HTTPValidationError]]:
    """Get job status.

     Get the status of a job.

    Args:
        job_id (str): ID of the job, e.g. `uncertainty-rk-family-am-reflections-jo`
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet, HTTPValidationError]
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
        token=token,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: Client,
    token: str,
) -> Response[Union[GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet, HTTPValidationError]]:
    """Get job status.

     Get the status of a job.

    Args:
        job_id (str): ID of the job, e.g. `uncertainty-rk-family-am-reflections-jo`
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
        client=client,
        token=token,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_id: str,
    *,
    client: Client,
    token: str,
) -> Optional[Union[GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet, HTTPValidationError]]:
    """Get job status.

     Get the status of a job.

    Args:
        job_id (str): ID of the job, e.g. `uncertainty-rk-family-am-reflections-jo`
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetJobApiV2JobsStatusJobIdGetResponseGetJobApiV2JobsStatusJobIdGet, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
            token=token,
        )
    ).parsed
