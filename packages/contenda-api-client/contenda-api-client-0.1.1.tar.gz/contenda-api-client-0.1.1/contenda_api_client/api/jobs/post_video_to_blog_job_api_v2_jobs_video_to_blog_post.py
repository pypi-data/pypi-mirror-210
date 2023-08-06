from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.http_validation_error import HTTPValidationError
from ...models.job_create_video_to_blog import JobCreateVideoToBlog
from ...models.post_video_to_blog_job_api_v2_jobs_video_to_blog_post_response_post_video_to_blog_job_api_v2_jobs_video_to_blog_post import (
    PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost,
)
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client: Client,
    json_body: JobCreateVideoToBlog,
    token: str,
) -> Dict[str, Any]:
    url = "{}/api/v2/jobs/video-to-blog".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["token"] = token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
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
        PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost,
    ]
]:
    if response.status_code == HTTPStatus.OK:
        response_200 = (
            PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost.from_dict(
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
        HTTPValidationError,
        PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost,
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
    json_body: JobCreateVideoToBlog,
    token: str,
) -> Response[
    Union[
        HTTPValidationError,
        PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost,
    ]
]:
    r"""Create a video-to-blog job.

     Create a video-to-blog job.

    **Request body:**
    - `source_id` (`string`): media source ID formatted, e.g. `youtube dQw4w9WgXcQ` - the platform name,
    space,
        then the media ID on that platform
    - `status_update_email` (`string`): (optional) e-mail address to send an update to whenever the
    status of the job
        changes, defaults to the queueing user's email
    - `status_update_webhook_url` (`string`): (optional) a webhook to be called with a POST
        request whenever the status of the job changes
    - `type` (`string`): video-to-blog job type, can be `presentation` or `tutorial`
    - `overrides` (`dict`): (optional) overrides for the job type. Any overrides not specified will use
    the default.

    **Source ID types:**

    These are the supported `source_id` types - substitute the `$values` for your media:

    - `youtube $id` YouTube videos, $id for a YouTube video ID, e.g.
    https://www.youtube.com/watch?v=dQw4w9WgXcQ becomes `youtube dQw4w9WgXcQ`
    - `twitch $id` Twitch vods, $id for a Twitch vod ID, e.g. https://www.twitch.tv/videos/1079879708
    becomes `twitch 1079879708`
    - `facebook $channel $id` Facebook videos, $channel for a Facebook page ID and $id for a Facebook
    video ID on that page, e.g. https://www.facebook.com/PersonOfInterestTV/videos/1827475693951431
    becomes `facebook PersonOfInterestTV 1827475693951431`
    - `mux $id` Mux videos, $id for a Mux video ID, e.g.
    https://stream.mux.com/uNbxnGLKJ00yfbijDO8COxTOyVKT01xpxW.m3u8 becomes `mux
    uNbxnGLKJ00yfbijDO8COxTOyVKT01xpxW`
    - `url $url` Raw URL links, $url for a fully qualified URL that would download a media, e.g. `url
    https://download.blender.org/demo/movies/BBB/bbb_sunflower_1080p_60fps_normal.mp4`

    **Overrides:**

    *Please note that this is an experimental feature, and we can't currently provide support for it.*

    Overrides are set under three segment type keys: `body_segment`, `heading_segment`, and
    `question_segment`.
    The `body_segment` will define the generation parameters for the body of the blog post, the
    `heading_segment` will
    define the generation parameters for the heading of the blog post. The `question_segment` is
    currently unused.

    Each segment type has the following parameters:
    - `prompt_template_string` (`string`): (optional) a template string to use as the prompt for the
    generation. The
        transcript will be inserted into the template string at the `{TEXT}` placeholder. Takes
    precedence over
        `prompt_template_name`.
    - `prompt_template_name` (`string`): (optional) the filename of an internal template to use as the
    prompt for the
        generation. (These are for internal use only, and are not currently documented.)
    - `system_message_string` (`string`): (optional) a system message to use as the prompt for the
    generation. Takes
        precedence over `system_message_name`.
    - `system_message_name` (`string`): (optional) the filename of an internal system message to use as
    the prompt for
        the generation. (These are for internal use only, and are not currently documented.)
    - `completion_max_tokens` (`int`): (optional) the maximum number of tokens to generate for the
    segment.
    - `temperature` (`float`): (optional) the temperature to use for the generation.
    - `regeneration_fn` (`string`): (optional) the name of a function to use to regenerate the segment.
        (These are for internal use only, and are not currently documented.)
    - `regeneration_tries` (`int`): (optional) the number of times to try regenerating the segment if
    the generated
        text is below the `regeneration_threshold`.
    - `regeneration_threshold` (`float`): (optional) the threshold for the generated text to be above to
    be considered
        valid. If the generated text is below this threshold, the segment will be regenerated up to
    `regeneration_tries`

    For example, to override the `body_segment`, you would use the following in your request body:
    ```
    {
        ...
        \"overrides\": {
            \"body_segment\": {
               \"prompt_template_string\": \"Turn the following transcript into a blog post: {TEXT}\",
               \"system_message_string\": \"Make a great blog!\"
               \"completion_max_tokens\": 800,
               \"temperature\": 0.7,
               \"regeneration_tries\": 0,
               \"regeneration_threshold\": 1.0,
            }
        }
    }
    ```

    Args:
        token (str):
        json_body (JobCreateVideoToBlog): Video to blog job creation model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost]]
    """

    kwargs = _get_kwargs(
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
    *,
    client: Client,
    json_body: JobCreateVideoToBlog,
    token: str,
) -> Optional[
    Union[
        HTTPValidationError,
        PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost,
    ]
]:
    r"""Create a video-to-blog job.

     Create a video-to-blog job.

    **Request body:**
    - `source_id` (`string`): media source ID formatted, e.g. `youtube dQw4w9WgXcQ` - the platform name,
    space,
        then the media ID on that platform
    - `status_update_email` (`string`): (optional) e-mail address to send an update to whenever the
    status of the job
        changes, defaults to the queueing user's email
    - `status_update_webhook_url` (`string`): (optional) a webhook to be called with a POST
        request whenever the status of the job changes
    - `type` (`string`): video-to-blog job type, can be `presentation` or `tutorial`
    - `overrides` (`dict`): (optional) overrides for the job type. Any overrides not specified will use
    the default.

    **Source ID types:**

    These are the supported `source_id` types - substitute the `$values` for your media:

    - `youtube $id` YouTube videos, $id for a YouTube video ID, e.g.
    https://www.youtube.com/watch?v=dQw4w9WgXcQ becomes `youtube dQw4w9WgXcQ`
    - `twitch $id` Twitch vods, $id for a Twitch vod ID, e.g. https://www.twitch.tv/videos/1079879708
    becomes `twitch 1079879708`
    - `facebook $channel $id` Facebook videos, $channel for a Facebook page ID and $id for a Facebook
    video ID on that page, e.g. https://www.facebook.com/PersonOfInterestTV/videos/1827475693951431
    becomes `facebook PersonOfInterestTV 1827475693951431`
    - `mux $id` Mux videos, $id for a Mux video ID, e.g.
    https://stream.mux.com/uNbxnGLKJ00yfbijDO8COxTOyVKT01xpxW.m3u8 becomes `mux
    uNbxnGLKJ00yfbijDO8COxTOyVKT01xpxW`
    - `url $url` Raw URL links, $url for a fully qualified URL that would download a media, e.g. `url
    https://download.blender.org/demo/movies/BBB/bbb_sunflower_1080p_60fps_normal.mp4`

    **Overrides:**

    *Please note that this is an experimental feature, and we can't currently provide support for it.*

    Overrides are set under three segment type keys: `body_segment`, `heading_segment`, and
    `question_segment`.
    The `body_segment` will define the generation parameters for the body of the blog post, the
    `heading_segment` will
    define the generation parameters for the heading of the blog post. The `question_segment` is
    currently unused.

    Each segment type has the following parameters:
    - `prompt_template_string` (`string`): (optional) a template string to use as the prompt for the
    generation. The
        transcript will be inserted into the template string at the `{TEXT}` placeholder. Takes
    precedence over
        `prompt_template_name`.
    - `prompt_template_name` (`string`): (optional) the filename of an internal template to use as the
    prompt for the
        generation. (These are for internal use only, and are not currently documented.)
    - `system_message_string` (`string`): (optional) a system message to use as the prompt for the
    generation. Takes
        precedence over `system_message_name`.
    - `system_message_name` (`string`): (optional) the filename of an internal system message to use as
    the prompt for
        the generation. (These are for internal use only, and are not currently documented.)
    - `completion_max_tokens` (`int`): (optional) the maximum number of tokens to generate for the
    segment.
    - `temperature` (`float`): (optional) the temperature to use for the generation.
    - `regeneration_fn` (`string`): (optional) the name of a function to use to regenerate the segment.
        (These are for internal use only, and are not currently documented.)
    - `regeneration_tries` (`int`): (optional) the number of times to try regenerating the segment if
    the generated
        text is below the `regeneration_threshold`.
    - `regeneration_threshold` (`float`): (optional) the threshold for the generated text to be above to
    be considered
        valid. If the generated text is below this threshold, the segment will be regenerated up to
    `regeneration_tries`

    For example, to override the `body_segment`, you would use the following in your request body:
    ```
    {
        ...
        \"overrides\": {
            \"body_segment\": {
               \"prompt_template_string\": \"Turn the following transcript into a blog post: {TEXT}\",
               \"system_message_string\": \"Make a great blog!\"
               \"completion_max_tokens\": 800,
               \"temperature\": 0.7,
               \"regeneration_tries\": 0,
               \"regeneration_threshold\": 1.0,
            }
        }
    }
    ```

    Args:
        token (str):
        json_body (JobCreateVideoToBlog): Video to blog job creation model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
        token=token,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: JobCreateVideoToBlog,
    token: str,
) -> Response[
    Union[
        HTTPValidationError,
        PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost,
    ]
]:
    r"""Create a video-to-blog job.

     Create a video-to-blog job.

    **Request body:**
    - `source_id` (`string`): media source ID formatted, e.g. `youtube dQw4w9WgXcQ` - the platform name,
    space,
        then the media ID on that platform
    - `status_update_email` (`string`): (optional) e-mail address to send an update to whenever the
    status of the job
        changes, defaults to the queueing user's email
    - `status_update_webhook_url` (`string`): (optional) a webhook to be called with a POST
        request whenever the status of the job changes
    - `type` (`string`): video-to-blog job type, can be `presentation` or `tutorial`
    - `overrides` (`dict`): (optional) overrides for the job type. Any overrides not specified will use
    the default.

    **Source ID types:**

    These are the supported `source_id` types - substitute the `$values` for your media:

    - `youtube $id` YouTube videos, $id for a YouTube video ID, e.g.
    https://www.youtube.com/watch?v=dQw4w9WgXcQ becomes `youtube dQw4w9WgXcQ`
    - `twitch $id` Twitch vods, $id for a Twitch vod ID, e.g. https://www.twitch.tv/videos/1079879708
    becomes `twitch 1079879708`
    - `facebook $channel $id` Facebook videos, $channel for a Facebook page ID and $id for a Facebook
    video ID on that page, e.g. https://www.facebook.com/PersonOfInterestTV/videos/1827475693951431
    becomes `facebook PersonOfInterestTV 1827475693951431`
    - `mux $id` Mux videos, $id for a Mux video ID, e.g.
    https://stream.mux.com/uNbxnGLKJ00yfbijDO8COxTOyVKT01xpxW.m3u8 becomes `mux
    uNbxnGLKJ00yfbijDO8COxTOyVKT01xpxW`
    - `url $url` Raw URL links, $url for a fully qualified URL that would download a media, e.g. `url
    https://download.blender.org/demo/movies/BBB/bbb_sunflower_1080p_60fps_normal.mp4`

    **Overrides:**

    *Please note that this is an experimental feature, and we can't currently provide support for it.*

    Overrides are set under three segment type keys: `body_segment`, `heading_segment`, and
    `question_segment`.
    The `body_segment` will define the generation parameters for the body of the blog post, the
    `heading_segment` will
    define the generation parameters for the heading of the blog post. The `question_segment` is
    currently unused.

    Each segment type has the following parameters:
    - `prompt_template_string` (`string`): (optional) a template string to use as the prompt for the
    generation. The
        transcript will be inserted into the template string at the `{TEXT}` placeholder. Takes
    precedence over
        `prompt_template_name`.
    - `prompt_template_name` (`string`): (optional) the filename of an internal template to use as the
    prompt for the
        generation. (These are for internal use only, and are not currently documented.)
    - `system_message_string` (`string`): (optional) a system message to use as the prompt for the
    generation. Takes
        precedence over `system_message_name`.
    - `system_message_name` (`string`): (optional) the filename of an internal system message to use as
    the prompt for
        the generation. (These are for internal use only, and are not currently documented.)
    - `completion_max_tokens` (`int`): (optional) the maximum number of tokens to generate for the
    segment.
    - `temperature` (`float`): (optional) the temperature to use for the generation.
    - `regeneration_fn` (`string`): (optional) the name of a function to use to regenerate the segment.
        (These are for internal use only, and are not currently documented.)
    - `regeneration_tries` (`int`): (optional) the number of times to try regenerating the segment if
    the generated
        text is below the `regeneration_threshold`.
    - `regeneration_threshold` (`float`): (optional) the threshold for the generated text to be above to
    be considered
        valid. If the generated text is below this threshold, the segment will be regenerated up to
    `regeneration_tries`

    For example, to override the `body_segment`, you would use the following in your request body:
    ```
    {
        ...
        \"overrides\": {
            \"body_segment\": {
               \"prompt_template_string\": \"Turn the following transcript into a blog post: {TEXT}\",
               \"system_message_string\": \"Make a great blog!\"
               \"completion_max_tokens\": 800,
               \"temperature\": 0.7,
               \"regeneration_tries\": 0,
               \"regeneration_threshold\": 1.0,
            }
        }
    }
    ```

    Args:
        token (str):
        json_body (JobCreateVideoToBlog): Video to blog job creation model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost]]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        token=token,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    json_body: JobCreateVideoToBlog,
    token: str,
) -> Optional[
    Union[
        HTTPValidationError,
        PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost,
    ]
]:
    r"""Create a video-to-blog job.

     Create a video-to-blog job.

    **Request body:**
    - `source_id` (`string`): media source ID formatted, e.g. `youtube dQw4w9WgXcQ` - the platform name,
    space,
        then the media ID on that platform
    - `status_update_email` (`string`): (optional) e-mail address to send an update to whenever the
    status of the job
        changes, defaults to the queueing user's email
    - `status_update_webhook_url` (`string`): (optional) a webhook to be called with a POST
        request whenever the status of the job changes
    - `type` (`string`): video-to-blog job type, can be `presentation` or `tutorial`
    - `overrides` (`dict`): (optional) overrides for the job type. Any overrides not specified will use
    the default.

    **Source ID types:**

    These are the supported `source_id` types - substitute the `$values` for your media:

    - `youtube $id` YouTube videos, $id for a YouTube video ID, e.g.
    https://www.youtube.com/watch?v=dQw4w9WgXcQ becomes `youtube dQw4w9WgXcQ`
    - `twitch $id` Twitch vods, $id for a Twitch vod ID, e.g. https://www.twitch.tv/videos/1079879708
    becomes `twitch 1079879708`
    - `facebook $channel $id` Facebook videos, $channel for a Facebook page ID and $id for a Facebook
    video ID on that page, e.g. https://www.facebook.com/PersonOfInterestTV/videos/1827475693951431
    becomes `facebook PersonOfInterestTV 1827475693951431`
    - `mux $id` Mux videos, $id for a Mux video ID, e.g.
    https://stream.mux.com/uNbxnGLKJ00yfbijDO8COxTOyVKT01xpxW.m3u8 becomes `mux
    uNbxnGLKJ00yfbijDO8COxTOyVKT01xpxW`
    - `url $url` Raw URL links, $url for a fully qualified URL that would download a media, e.g. `url
    https://download.blender.org/demo/movies/BBB/bbb_sunflower_1080p_60fps_normal.mp4`

    **Overrides:**

    *Please note that this is an experimental feature, and we can't currently provide support for it.*

    Overrides are set under three segment type keys: `body_segment`, `heading_segment`, and
    `question_segment`.
    The `body_segment` will define the generation parameters for the body of the blog post, the
    `heading_segment` will
    define the generation parameters for the heading of the blog post. The `question_segment` is
    currently unused.

    Each segment type has the following parameters:
    - `prompt_template_string` (`string`): (optional) a template string to use as the prompt for the
    generation. The
        transcript will be inserted into the template string at the `{TEXT}` placeholder. Takes
    precedence over
        `prompt_template_name`.
    - `prompt_template_name` (`string`): (optional) the filename of an internal template to use as the
    prompt for the
        generation. (These are for internal use only, and are not currently documented.)
    - `system_message_string` (`string`): (optional) a system message to use as the prompt for the
    generation. Takes
        precedence over `system_message_name`.
    - `system_message_name` (`string`): (optional) the filename of an internal system message to use as
    the prompt for
        the generation. (These are for internal use only, and are not currently documented.)
    - `completion_max_tokens` (`int`): (optional) the maximum number of tokens to generate for the
    segment.
    - `temperature` (`float`): (optional) the temperature to use for the generation.
    - `regeneration_fn` (`string`): (optional) the name of a function to use to regenerate the segment.
        (These are for internal use only, and are not currently documented.)
    - `regeneration_tries` (`int`): (optional) the number of times to try regenerating the segment if
    the generated
        text is below the `regeneration_threshold`.
    - `regeneration_threshold` (`float`): (optional) the threshold for the generated text to be above to
    be considered
        valid. If the generated text is below this threshold, the segment will be regenerated up to
    `regeneration_tries`

    For example, to override the `body_segment`, you would use the following in your request body:
    ```
    {
        ...
        \"overrides\": {
            \"body_segment\": {
               \"prompt_template_string\": \"Turn the following transcript into a blog post: {TEXT}\",
               \"system_message_string\": \"Make a great blog!\"
               \"completion_max_tokens\": 800,
               \"temperature\": 0.7,
               \"regeneration_tries\": 0,
               \"regeneration_threshold\": 1.0,
            }
        }
    }
    ```

    Args:
        token (str):
        json_body (JobCreateVideoToBlog): Video to blog job creation model.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PostVideoToBlogJobApiV2JobsVideoToBlogPostResponsePostVideoToBlogJobApiV2JobsVideoToBlogPost]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
            token=token,
        )
    ).parsed
