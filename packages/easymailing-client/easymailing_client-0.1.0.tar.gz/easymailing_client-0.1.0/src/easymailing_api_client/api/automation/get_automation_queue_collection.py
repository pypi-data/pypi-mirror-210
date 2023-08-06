from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.get_automation_queue_collection_response_200 import GetAutomationQueueCollectionResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    page: Union[Unset, None, int] = 1,
) -> Dict[str, Any]:
    url = "{}/automation_queues".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["page"] = page

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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[GetAutomationQueueCollectionResponse200]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetAutomationQueueCollectionResponse200.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[GetAutomationQueueCollectionResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    page: Union[Unset, None, int] = 1,
) -> Response[GetAutomationQueueCollectionResponse200]:
    """Retrieves the collection of AutomationQueue resources.

     Retrieves the collection of AutomationQueue resources.

    Args:
        page (Union[Unset, None, int]):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAutomationQueueCollectionResponse200]
    """

    kwargs = _get_kwargs(
        client=client,
        page=page,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    page: Union[Unset, None, int] = 1,
) -> Optional[GetAutomationQueueCollectionResponse200]:
    """Retrieves the collection of AutomationQueue resources.

     Retrieves the collection of AutomationQueue resources.

    Args:
        page (Union[Unset, None, int]):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAutomationQueueCollectionResponse200
    """

    return sync_detailed(
        client=client,
        page=page,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    page: Union[Unset, None, int] = 1,
) -> Response[GetAutomationQueueCollectionResponse200]:
    """Retrieves the collection of AutomationQueue resources.

     Retrieves the collection of AutomationQueue resources.

    Args:
        page (Union[Unset, None, int]):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetAutomationQueueCollectionResponse200]
    """

    kwargs = _get_kwargs(
        client=client,
        page=page,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    page: Union[Unset, None, int] = 1,
) -> Optional[GetAutomationQueueCollectionResponse200]:
    """Retrieves the collection of AutomationQueue resources.

     Retrieves the collection of AutomationQueue resources.

    Args:
        page (Union[Unset, None, int]):  Default: 1.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetAutomationQueueCollectionResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
        )
    ).parsed
