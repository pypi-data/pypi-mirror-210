from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.subdomain_with_detail import SubdomainWithDetail
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: int,
    *,
    client: AuthenticatedClient,
    only_online: Union[Unset, None, bool] = UNSET,
    only_primary: Union[Unset, None, bool] = UNSET,
) -> Dict[str, Any]:
    url = "{}/api/programs/{id}/subdomain/get/details/".format(client.base_url, id=id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["only_online"] = only_online

    params["only_primary"] = only_primary

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


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[List["SubdomainWithDetail"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = SubdomainWithDetail.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[List["SubdomainWithDetail"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: int,
    *,
    client: AuthenticatedClient,
    only_online: Union[Unset, None, bool] = UNSET,
    only_primary: Union[Unset, None, bool] = UNSET,
) -> Response[List["SubdomainWithDetail"]]:
    """
    Args:
        id (int):
        only_online (Union[Unset, None, bool]):
        only_primary (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['SubdomainWithDetail']]
    """

    kwargs = _get_kwargs(
        id=id,
        client=client,
        only_online=only_online,
        only_primary=only_primary,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient,
    only_online: Union[Unset, None, bool] = UNSET,
    only_primary: Union[Unset, None, bool] = UNSET,
) -> Optional[List["SubdomainWithDetail"]]:
    """
    Args:
        id (int):
        only_online (Union[Unset, None, bool]):
        only_primary (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['SubdomainWithDetail']
    """

    return sync_detailed(
        id=id,
        client=client,
        only_online=only_online,
        only_primary=only_primary,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient,
    only_online: Union[Unset, None, bool] = UNSET,
    only_primary: Union[Unset, None, bool] = UNSET,
) -> Response[List["SubdomainWithDetail"]]:
    """
    Args:
        id (int):
        only_online (Union[Unset, None, bool]):
        only_primary (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['SubdomainWithDetail']]
    """

    kwargs = _get_kwargs(
        id=id,
        client=client,
        only_online=only_online,
        only_primary=only_primary,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient,
    only_online: Union[Unset, None, bool] = UNSET,
    only_primary: Union[Unset, None, bool] = UNSET,
) -> Optional[List["SubdomainWithDetail"]]:
    """
    Args:
        id (int):
        only_online (Union[Unset, None, bool]):
        only_primary (Union[Unset, None, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['SubdomainWithDetail']
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            only_online=only_online,
            only_primary=only_primary,
        )
    ).parsed
