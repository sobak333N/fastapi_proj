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