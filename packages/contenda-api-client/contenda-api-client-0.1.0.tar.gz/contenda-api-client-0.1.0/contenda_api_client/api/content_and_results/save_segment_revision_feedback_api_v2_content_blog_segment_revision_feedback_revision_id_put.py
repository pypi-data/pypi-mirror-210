from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.http_validation_error import HTTPValidationError
from ...models.save_segment_revision_feedback_api_v2_content_blog_segment_revision_feedback_revision_id_put_response_save_segment_revision_feedback_api_v2_content_blog_segment_revision_feedback_revision_id_put import (
    SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut,
)
from ...models.segment_revision_feedback_request_model import SegmentRevisionFeedbackRequestModel
from ...types import UNSET, Response


def _get_kwargs(
    revision_id: str,
    *,
    client: Client,
    json_body: SegmentRevisionFeedbackRequestModel,
    token: str,
) -> Dict[str, Any]:
    url = "{}/api/v2/content/blog/segment/revision/feedback/{revision_id}".format(
        client.base_url, revision_id=revision_id
    )

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["token"] = token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "method": "put",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "json": json_json_body,
        "params": params,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[
    Union[
        HTTPValidationError,
        SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut,
    ]
]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut.from_dict(
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
    Union[
        HTTPValidationError,
        SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    revision_id: str,
    *,
    client: Client,
    json_body: SegmentRevisionFeedbackRequestModel,
    token: str,
) -> Response[
    Union[
        HTTPValidationError,
        SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut,
    ]
]:
    """Save feedback for a regenerated segment.

     Save feedback for why a segment was regenerated.

    The labels to use for feedback is given by the endpoint `GET
    /api/v2/content/blog/segment/revision/feedback-options`

    Args:
        revision_id (str): ID of the segment revision in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`. This ID can be found after regenerating a segment.
        token (str):
        json_body (SegmentRevisionFeedbackRequestModel): Response model for the body input of
            saving segment revisions after regeneration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut]]
    """

    kwargs = _get_kwargs(
        revision_id=revision_id,
        client=client,
        json_body=json_body,
        token=token,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    revision_id: str,
    *,
    client: Client,
    json_body: SegmentRevisionFeedbackRequestModel,
    token: str,
) -> Optional[
    Union[
        HTTPValidationError,
        SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut,
    ]
]:
    """Save feedback for a regenerated segment.

     Save feedback for why a segment was regenerated.

    The labels to use for feedback is given by the endpoint `GET
    /api/v2/content/blog/segment/revision/feedback-options`

    Args:
        revision_id (str): ID of the segment revision in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`. This ID can be found after regenerating a segment.
        token (str):
        json_body (SegmentRevisionFeedbackRequestModel): Response model for the body input of
            saving segment revisions after regeneration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut]
    """

    return sync_detailed(
        revision_id=revision_id,
        client=client,
        json_body=json_body,
        token=token,
    ).parsed


async def asyncio_detailed(
    revision_id: str,
    *,
    client: Client,
    json_body: SegmentRevisionFeedbackRequestModel,
    token: str,
) -> Response[
    Union[
        HTTPValidationError,
        SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut,
    ]
]:
    """Save feedback for a regenerated segment.

     Save feedback for why a segment was regenerated.

    The labels to use for feedback is given by the endpoint `GET
    /api/v2/content/blog/segment/revision/feedback-options`

    Args:
        revision_id (str): ID of the segment revision in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`. This ID can be found after regenerating a segment.
        token (str):
        json_body (SegmentRevisionFeedbackRequestModel): Response model for the body input of
            saving segment revisions after regeneration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut]]
    """

    kwargs = _get_kwargs(
        revision_id=revision_id,
        client=client,
        json_body=json_body,
        token=token,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    revision_id: str,
    *,
    client: Client,
    json_body: SegmentRevisionFeedbackRequestModel,
    token: str,
) -> Optional[
    Union[
        HTTPValidationError,
        SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut,
    ]
]:
    """Save feedback for a regenerated segment.

     Save feedback for why a segment was regenerated.

    The labels to use for feedback is given by the endpoint `GET
    /api/v2/content/blog/segment/revision/feedback-options`

    Args:
        revision_id (str): ID of the segment revision in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`. This ID can be found after regenerating a segment.
        token (str):
        json_body (SegmentRevisionFeedbackRequestModel): Response model for the body input of
            saving segment revisions after regeneration.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPutResponseSaveSegmentRevisionFeedbackApiV2ContentBlogSegmentRevisionFeedbackRevisionIdPut]
    """

    return (
        await asyncio_detailed(
            revision_id=revision_id,
            client=client,
            json_body=json_body,
            token=token,
        )
    ).parsed
