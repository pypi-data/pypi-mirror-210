from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.contenda_body_segment_save_request import ContendaBodySegmentSaveRequest
from ...models.contenda_code_segment_save_request import ContendaCodeSegmentSaveRequest
from ...models.contenda_heading_segment_save_request import ContendaHeadingSegmentSaveRequest
from ...models.contenda_image_segment_save_request import ContendaImageSegmentSaveRequest
from ...models.http_validation_error import HTTPValidationError
from ...models.save_blog_result_document_api_v2_content_blog_blog_id_put_response_save_blog_result_document_api_v2_content_blog_blog_id_put import (
    SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut,
)
from ...models.user_body_segment_save_request import UserBodySegmentSaveRequest
from ...models.user_code_segment_save_request import UserCodeSegmentSaveRequest
from ...models.user_heading_segment_save_request import UserHeadingSegmentSaveRequest
from ...types import UNSET, Response


def _get_kwargs(
    blog_id: str,
    *,
    client: Client,
    json_body: List[
        Union[
            "ContendaBodySegmentSaveRequest",
            "ContendaCodeSegmentSaveRequest",
            "ContendaHeadingSegmentSaveRequest",
            "ContendaImageSegmentSaveRequest",
            "UserBodySegmentSaveRequest",
            "UserCodeSegmentSaveRequest",
            "UserHeadingSegmentSaveRequest",
        ]
    ],
    token: str,
) -> Dict[str, Any]:
    url = "{}/api/v2/content/blog/{blog_id}".format(client.base_url, blog_id=blog_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["token"] = token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = []
    for json_body_item_data in json_body:
        json_body_item: Dict[str, Any]

        if isinstance(json_body_item_data, ContendaBodySegmentSaveRequest):
            json_body_item = json_body_item_data.to_dict()

        elif isinstance(json_body_item_data, ContendaHeadingSegmentSaveRequest):
            json_body_item = json_body_item_data.to_dict()

        elif isinstance(json_body_item_data, ContendaCodeSegmentSaveRequest):
            json_body_item = json_body_item_data.to_dict()

        elif isinstance(json_body_item_data, ContendaImageSegmentSaveRequest):
            json_body_item = json_body_item_data.to_dict()

        elif isinstance(json_body_item_data, UserBodySegmentSaveRequest):
            json_body_item = json_body_item_data.to_dict()

        elif isinstance(json_body_item_data, UserHeadingSegmentSaveRequest):
            json_body_item = json_body_item_data.to_dict()

        else:
            json_body_item = json_body_item_data.to_dict()

        json_json_body.append(json_body_item)

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
        SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut,
    ]
]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut.from_dict(
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
        SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut,
    ]
]:
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
    json_body: List[
        Union[
            "ContendaBodySegmentSaveRequest",
            "ContendaCodeSegmentSaveRequest",
            "ContendaHeadingSegmentSaveRequest",
            "ContendaImageSegmentSaveRequest",
            "UserBodySegmentSaveRequest",
            "UserCodeSegmentSaveRequest",
            "UserHeadingSegmentSaveRequest",
        ]
    ],
    token: str,
) -> Response[
    Union[
        HTTPValidationError,
        SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut,
    ]
]:
    """Save edits to a result blog.

     Save the given list of blog segment objects from the client request body as the resulting blog.

    Segment types `body`, `heading`, `image`, and `code` are segments created by Contenda.
    Look at the request body schema examples to see the required body fields given each `segment_type`.

    Edited or Keep as is?
    - include segment object with the updated field or with its original value!

    Addition
    - add a new segment object with a uuid generated `id` to the list of blog segemnt objects in your
    request
    - these must be of segment type `user_heading`, `user_body`, `user_code` as they are your added
    segments

    Deletions and Reordering
    - the blog is saved as given in the request, so any segment removed or reordered will do the trick!

    Args:
        blog_id (str): ID of the blog in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`
        token (str):
        json_body (List[Union['ContendaBodySegmentSaveRequest', 'ContendaCodeSegmentSaveRequest',
            'ContendaHeadingSegmentSaveRequest', 'ContendaImageSegmentSaveRequest',
            'UserBodySegmentSaveRequest', 'UserCodeSegmentSaveRequest',
            'UserHeadingSegmentSaveRequest']]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut]]
    """

    kwargs = _get_kwargs(
        blog_id=blog_id,
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
    blog_id: str,
    *,
    client: Client,
    json_body: List[
        Union[
            "ContendaBodySegmentSaveRequest",
            "ContendaCodeSegmentSaveRequest",
            "ContendaHeadingSegmentSaveRequest",
            "ContendaImageSegmentSaveRequest",
            "UserBodySegmentSaveRequest",
            "UserCodeSegmentSaveRequest",
            "UserHeadingSegmentSaveRequest",
        ]
    ],
    token: str,
) -> Optional[
    Union[
        HTTPValidationError,
        SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut,
    ]
]:
    """Save edits to a result blog.

     Save the given list of blog segment objects from the client request body as the resulting blog.

    Segment types `body`, `heading`, `image`, and `code` are segments created by Contenda.
    Look at the request body schema examples to see the required body fields given each `segment_type`.

    Edited or Keep as is?
    - include segment object with the updated field or with its original value!

    Addition
    - add a new segment object with a uuid generated `id` to the list of blog segemnt objects in your
    request
    - these must be of segment type `user_heading`, `user_body`, `user_code` as they are your added
    segments

    Deletions and Reordering
    - the blog is saved as given in the request, so any segment removed or reordered will do the trick!

    Args:
        blog_id (str): ID of the blog in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`
        token (str):
        json_body (List[Union['ContendaBodySegmentSaveRequest', 'ContendaCodeSegmentSaveRequest',
            'ContendaHeadingSegmentSaveRequest', 'ContendaImageSegmentSaveRequest',
            'UserBodySegmentSaveRequest', 'UserCodeSegmentSaveRequest',
            'UserHeadingSegmentSaveRequest']]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut]
    """

    return sync_detailed(
        blog_id=blog_id,
        client=client,
        json_body=json_body,
        token=token,
    ).parsed


async def asyncio_detailed(
    blog_id: str,
    *,
    client: Client,
    json_body: List[
        Union[
            "ContendaBodySegmentSaveRequest",
            "ContendaCodeSegmentSaveRequest",
            "ContendaHeadingSegmentSaveRequest",
            "ContendaImageSegmentSaveRequest",
            "UserBodySegmentSaveRequest",
            "UserCodeSegmentSaveRequest",
            "UserHeadingSegmentSaveRequest",
        ]
    ],
    token: str,
) -> Response[
    Union[
        HTTPValidationError,
        SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut,
    ]
]:
    """Save edits to a result blog.

     Save the given list of blog segment objects from the client request body as the resulting blog.

    Segment types `body`, `heading`, `image`, and `code` are segments created by Contenda.
    Look at the request body schema examples to see the required body fields given each `segment_type`.

    Edited or Keep as is?
    - include segment object with the updated field or with its original value!

    Addition
    - add a new segment object with a uuid generated `id` to the list of blog segemnt objects in your
    request
    - these must be of segment type `user_heading`, `user_body`, `user_code` as they are your added
    segments

    Deletions and Reordering
    - the blog is saved as given in the request, so any segment removed or reordered will do the trick!

    Args:
        blog_id (str): ID of the blog in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`
        token (str):
        json_body (List[Union['ContendaBodySegmentSaveRequest', 'ContendaCodeSegmentSaveRequest',
            'ContendaHeadingSegmentSaveRequest', 'ContendaImageSegmentSaveRequest',
            'UserBodySegmentSaveRequest', 'UserCodeSegmentSaveRequest',
            'UserHeadingSegmentSaveRequest']]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut]]
    """

    kwargs = _get_kwargs(
        blog_id=blog_id,
        client=client,
        json_body=json_body,
        token=token,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    blog_id: str,
    *,
    client: Client,
    json_body: List[
        Union[
            "ContendaBodySegmentSaveRequest",
            "ContendaCodeSegmentSaveRequest",
            "ContendaHeadingSegmentSaveRequest",
            "ContendaImageSegmentSaveRequest",
            "UserBodySegmentSaveRequest",
            "UserCodeSegmentSaveRequest",
            "UserHeadingSegmentSaveRequest",
        ]
    ],
    token: str,
) -> Optional[
    Union[
        HTTPValidationError,
        SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut,
    ]
]:
    """Save edits to a result blog.

     Save the given list of blog segment objects from the client request body as the resulting blog.

    Segment types `body`, `heading`, `image`, and `code` are segments created by Contenda.
    Look at the request body schema examples to see the required body fields given each `segment_type`.

    Edited or Keep as is?
    - include segment object with the updated field or with its original value!

    Addition
    - add a new segment object with a uuid generated `id` to the list of blog segemnt objects in your
    request
    - these must be of segment type `user_heading`, `user_body`, `user_code` as they are your added
    segments

    Deletions and Reordering
    - the blog is saved as given in the request, so any segment removed or reordered will do the trick!

    Args:
        blog_id (str): ID of the blog in a `uuid4` format, e.g.
            `9ec1ff50-add4-402c-8656-c9147539cd4c`
        token (str):
        json_body (List[Union['ContendaBodySegmentSaveRequest', 'ContendaCodeSegmentSaveRequest',
            'ContendaHeadingSegmentSaveRequest', 'ContendaImageSegmentSaveRequest',
            'UserBodySegmentSaveRequest', 'UserCodeSegmentSaveRequest',
            'UserHeadingSegmentSaveRequest']]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SaveBlogResultDocumentApiV2ContentBlogBlogIdPutResponseSaveBlogResultDocumentApiV2ContentBlogBlogIdPut]
    """

    return (
        await asyncio_detailed(
            blog_id=blog_id,
            client=client,
            json_body=json_body,
            token=token,
        )
    ).parsed
