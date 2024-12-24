from httpx import AsyncClient, Cookies
import pytest
import asyncio
import logging

from tests.conftest import signup_instructor_data, logger


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_data",
    [
        ("credentials", "passwords",)
    ]
)
async def test_auth_tokens(test_data, request):
    # logger.disabled(logging.DEBUG)
    async with AsyncClient(base_url="http://nginx/api/v1", cookies=Cookies()) as async_client:
    # async with AsyncClient(base_url="http://nginx/api/v1", cookies=Cookies()) as async_client:

        credentials = request.getfixturevalue("credentials")
        passwords = request.getfixturevalue("passwords")


        invalid_payload = credentials["invalid"]
        logger.warning(invalid_payload)
        response = await async_client.post("/auth/login", json=invalid_payload)
        assert response.status_code == 401 


        valid_payload = credentials["valid"]
        response = await async_client.post("/auth/login", json=valid_payload)
        assert response.status_code == 200

        set_cookie_header = response.headers.get("set-cookie")
        assert set_cookie_header is not None, "Set-Cookie header is missing"
        refresh_token = [cookie.split("=")[1].split(";")[0] for cookie in set_cookie_header.split(",") if "refresh_token" in cookie][0]
        access_token = response.headers["Authorization"]
        old_refresh_token = refresh_token

        response = await async_client.post("/auth/login", json=valid_payload)
        assert response.status_code == 200

        set_cookie_header = response.headers.get("set-cookie")
        assert set_cookie_header is not None, "Set-Cookie header is missing"
        refresh_token = [cookie.split("=")[1].split(";")[0] for cookie in set_cookie_header.split(",") if "refresh_token" in cookie][0]
        assert old_refresh_token == refresh_token



        #  current-user TESTS
        response = await async_client.post(
            "/auth/current-user", 
            cookies={"refresh_token": refresh_token},
            headers={"Authorization": access_token}
        )
        assert response.status_code == 200
        logger.critical(response.__dict__)


        response = await async_client.post(
            "/auth/current-user", 
            cookies={"refresh_token": refresh_token},
            headers={}
        )
        assert response.status_code == 403
        logger.critical(response.__dict__)


        response = await async_client.post(
            "/auth/current-user", 
            cookies={"refresh_token": refresh_token},
            headers={"Authorization": "asdasdasdasdasd"}
        )
        assert response.status_code == 403
        logger.critical(response.__dict__)


        set_cookie_header = response.headers.get("set-cookie")
        assert set_cookie_header is None

        # WAITING FOR ACCESS TOKEN EXPIRATION 
        # await asyncio.sleep(60)

        # response = await async_client.post(
        #     "/auth/current-user", 
        #     cookies={"refresh_token": refresh_token},
        #     headers={"Authorization": access_token}
        # )
        # assert response.status_code == 401


        # REFRESH_TOKEN

        response = await async_client.post(
            "/auth/refresh", 
            cookies={"refresh_token": "no-valid"},
        )
        assert response.status_code == 401


        response = await async_client.post(
            "/auth/refresh", 
            cookies={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        access_token = response.headers["Authorization"]


        response = await async_client.post(
            "/auth/current-user", 
            cookies={"refresh_token": refresh_token},
            headers={"Authorization": access_token}
        )
        assert response.status_code == 200

        # CHANGE-PASSWORD
        response = await async_client.post(
            "/auth/change-password", 
            json=passwords["valid"][0],
            headers={}
        )
        assert response.status_code == 401 or response.status_code == 403

        response = await async_client.post(
            "/auth/change-password", 
            json=passwords["valid"][0],
            headers={"Authorization": b"Bearer: NO-VALID"},
        )
        assert response.status_code == 401 or response.status_code == 403


        for payload in passwords["invalid"]:
            response = await async_client.post(
                "/auth/change-password", 
                cookies={"refresh_token": refresh_token},
                headers={"Authorization": access_token},
                json=payload,
            )
            assert response.status_code == 422 or response.status_code == 401


        # CREATE-NEW-ADMIN (WITHOUT RIGHTS)
        response = await async_client.post(
            "/auth/create-new-admin", 
            json={"test": "test"},
            headers={"Authorization": b"Bearer: NO-VALID"},
        )
        assert response.status_code == 403

        # LOGOUT

        response = await async_client.post(
            "/auth/logout", 
            headers={"Authorization": b"no-valid"},
        )
        assert response.status_code == 401 or response.status_code == 403


        response = await async_client.post(
            "/auth/logout", 
            headers={"Authorization": access_token},
            cookies={"refresh_token": "no-valid"},
        )
        assert response.status_code == 401 


        response = await async_client.post(
            "/auth/logout", 
            headers={"Authorization": access_token},
            cookies={"refresh_token": refresh_token},
        )
        assert response.status_code == 200


        response = await async_client.post(
            "/auth/current-user", 
            cookies={"refresh_token": refresh_token},
            headers={"Authorization": access_token}
        )
        assert response.status_code == 401


        response = await async_client.post(
            "/auth/refresh", 
            cookies={"refresh_token": refresh_token},
        )
        assert response.status_code == 401