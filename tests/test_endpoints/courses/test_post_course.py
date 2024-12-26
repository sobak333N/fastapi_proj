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
        ("credentials", "post_course")
    ]
)
async def test_post_course(test_data, request):
    async with AsyncClient(base_url="http://nginx/api/v1", cookies=Cookies()) as async_client:

        credentials = request.getfixturevalue("credentials")
        post_course_data = request.getfixturevalue("post_course")
        endpoint = post_course_data["endpoint"]

        student_valid_payload = credentials["valid"]["student"]
        refresh_token, access_token = await sign_in(student_valid_payload, async_client)

        response = await async_client.post(
            endpoint, 
            cookies={"refresh_token": refresh_token},
            headers={"Authorization": access_token}
        )
        assert response.status_code == 403

        await sign_out(refresh_token, access_token, async_client)

        instructor1_valid_payload = credentials["valid"]["instructor1"]
        refresh_token, access_token = await sign_in(instructor1_valid_payload, async_client)

        for payload in post_course_data["valid"]:
            response = await async_client.post(
                endpoint, 
                cookies={"refresh_token": refresh_token},
                headers={"Authorization": access_token},
                json=payload
            )
            assert response.status_code == 201

        for payload in post_course_data["invalid"]:
            response_locs = []
            error_code = payload["error_code"]
            payload.pop("error_code")
            if error_code == 422:
                validated = payload["locs"]
                payload.pop("locs")
            elif error_code == 404:
                validated = payload["message"]
                payload.pop("message")

            logger.critical(payload)
            response = await async_client.post(
                endpoint, 
                cookies={"refresh_token": refresh_token},
                headers={"Authorization": access_token},
                json=payload
            )
            assert response.status_code == error_code
            response_json = response.json()
            if error_code == 422:
                for detail in response_json["detail"]:
                    response_locs.append(detail["loc"][1])
            
                response_locs = sorted(response_locs)
                validated = sorted(validated)
                logger.critical(response_locs)
                logger.critical(validated)
                assert response_locs == validated
            elif error_code == 404:
                logger.critical(payload)
                logger.critical(response_json)
                assert response_json["message"] == validated
        await sign_out(refresh_token, access_token, async_client)
        
