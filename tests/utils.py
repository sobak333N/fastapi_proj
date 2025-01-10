from typing import Tuple

from httpx import AsyncClient, Cookies
import pytest
import asyncio


async def sign_in(payload: dict, async_client: AsyncClient) -> Tuple[str, str]:
    response = await async_client.post("/auth/login", json=payload)
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie")
    assert set_cookie_header is not None, "Set-Cookie header is missing"
    refresh_token = [cookie.split("=")[1].split(";")[0] for cookie in set_cookie_header.split(",") if "refresh_token" in cookie][0]
    access_token = response.headers["Authorization"]
    return (refresh_token, access_token)


async def sign_out(refresh_token: str, access_token: str, async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/auth/logout", 
        headers={"Authorization": access_token},
        cookies={"refresh_token": refresh_token},
    )
    assert response.status_code == 200


async def private_info(credentials_dict, endpoint: str, has_access, async_client):
    refresh_token, access_token = await sign_in(credentials_dict, async_client)
    response = await async_client.get(
        endpoint, 
        cookies={"refresh_token": refresh_token},
        headers={"Authorization": access_token},
    )
    assert response.status_code == 200
    response_json = response.json()
    if has_access:
        assert response_json.get("private_info", None) is not None
    else:
        assert response_json.get("private_info", None) is None

    await sign_out(refresh_token, access_token, async_client)