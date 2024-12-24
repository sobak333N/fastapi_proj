from httpx import AsyncClient, Cookies
import pytest
import asyncio
import logging

from tests.conftest import signup_instructor_data, logger
from tests.utils import sign_in, sign_out


@pytest.mark.skip(reason="temporary")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_data",
    [
        ("credentials", "passwords", "create_admin")
    ]
)
async def test_auth_tokens(test_data, request):
    # logger.disabled(logging.DEBUG)
    async with AsyncClient(base_url="http://nginx/api/v1", cookies=Cookies()) as async_client:
    # async with AsyncClient(base_url="http://nginx/api/v1", cookies=Cookies()) as async_client:

        credentials = request.getfixturevalue("credentials")
        passwords = request.getfixturevalue("passwords")
        create_admin = request.getfixturevalue("create_admin")

        invalid_payload = credentials["invalid"]
        response = await async_client.post("/auth/login", json=invalid_payload)
        assert response.status_code == 401 


        student_valid_payload = credentials["valid"]["student"]
        refresh_token, access_token = await sign_in(student_valid_payload, async_client)
        old_refresh_token = refresh_token
        refresh_token, access_token = await sign_in(student_valid_payload, async_client)
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

        response = await async_client.post(
            "/auth/create-new-admin", 
            json=create_admin["valid"][0],
            headers={"Authorization": access_token},
        )
        assert response.status_code == 403

        # LOGOUT

        response = await async_client.post(
            "/auth/logout", 
            headers={"Authorization": b"no-valid"},
        )
        assert response.status_code == 401 or response.status_code == 403


        await sign_out(refresh_token, access_token, async_client)


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

        # ADMIN ENPOINTS

        admin_valid_payload = credentials["valid"]["admin"]
        refresh_token, access_token = await sign_in(admin_valid_payload, async_client)



        for payload in create_admin["invalid"]:
            locs = payload["locs"]
            response_locs = []
            payload.pop("locs")

            response = await async_client.post(
                "/auth/create-new-admin", 
                cookies={"refresh_token": refresh_token},
                headers={"Authorization": access_token},
                json=payload,
            )
            assert response.status_code == 422 or response.status_code == 401
            response_json = response.json()
            for detail in response_json["detail"]:
                response_locs.append(detail["loc"][1])
            
            response_locs = sorted(response_locs)
            locs = sorted(locs)
            logger.critical(response_locs)
            logger.critical(locs)
            assert response_locs == locs

        for payload in create_admin["valid"]:
            response = await async_client.post(
                "/auth/create-new-admin", 
                cookies={"refresh_token": refresh_token},
                headers={"Authorization": access_token},
                json=payload,
            )
            assert response.status_code == 200


        await sign_out(refresh_token, access_token, async_client)

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