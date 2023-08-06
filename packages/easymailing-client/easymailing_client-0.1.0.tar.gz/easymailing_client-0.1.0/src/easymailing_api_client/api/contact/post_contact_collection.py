from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.contact_contact_input_jsonld_contact_write import ContactContactInputJsonldContactWrite
from ...models.contact_contact_output_jsonld_contact_read import ContactContactOutputJsonldContactRead
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: ContactContactInputJsonldContactWrite,
) -> Dict[str, Any]:
    url = "{}/contacts".format(client.base_url)

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
) -> Optional[Union[Any, ContactContactOutputJsonldContactRead]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = ContactContactOutputJsonldContactRead.from_dict(response.json())

        return response_201
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = cast(Any, None)
        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[Any, ContactContactOutputJsonldContactRead]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: ContactContactInputJsonldContactWrite,
) -> Response[Union[Any, ContactContactOutputJsonldContactRead]]:
    """Creates a Contact resource.

     Creates a Contact resource.

    Args:
        json_body (ContactContactInputJsonldContactWrite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ContactContactOutputJsonldContactRead]]
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
    json_body: ContactContactInputJsonldContactWrite,
) -> Optional[Union[Any, ContactContactOutputJsonldContactRead]]:
    """Creates a Contact resource.

     Creates a Contact resource.

    Args:
        json_body (ContactContactInputJsonldContactWrite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ContactContactOutputJsonldContactRead]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: ContactContactInputJsonldContactWrite,
) -> Response[Union[Any, ContactContactOutputJsonldContactRead]]:
    """Creates a Contact resource.

     Creates a Contact resource.

    Args:
        json_body (ContactContactInputJsonldContactWrite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ContactContactOutputJsonldContactRead]]
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
    json_body: ContactContactInputJsonldContactWrite,
) -> Optional[Union[Any, ContactContactOutputJsonldContactRead]]:
    """Creates a Contact resource.

     Creates a Contact resource.

    Args:
        json_body (ContactContactInputJsonldContactWrite):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ContactContactOutputJsonldContactRead]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
