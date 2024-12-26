from httpx import AsyncClient, Cookies
import pytest
import asyncio
import logging

from tests.conftest import signup_instructor_data, logger
from tests.utils import sign_in, sign_out


# @pytest.mark.skip(reason="temporary")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_data",
    [
        ("credentials", "update_course", "post_course")
    ]
)
async def test_update_course(test_data, request):
    async with AsyncClient(base_url="http://nginx/api/v1", cookies=Cookies()) as async_client:

        credentials = request.getfixturevalue("credentials")
        update_course_data = request.getfixturevalue("update_course")
        post_course_data = request.getfixturevalue("post_course")

        endpoint = update_course_data["endpoint"]

        student_valid_payload = credentials["valid"]["student"]
        logger.critical(student_valid_payload)
        refresh_token, access_token = await sign_in(student_valid_payload, async_client)

        logger.critical(f"{endpoint}/{update_course_data['valid'][0]['course_id']}")

        response = await async_client.patch(
            f"{endpoint}/{update_course_data['valid'][0]['course_id']}", 
            cookies={"refresh_token": refresh_token},
            headers={"Authorization": access_token},
            json=update_course_data['valid'][0]
        )
        assert response.status_code == 403

        await sign_out(refresh_token, access_token, async_client)

        instructor1_valid_payload = credentials["valid"]["instructor1"]
        refresh_token, access_token = await sign_in(instructor1_valid_payload, async_client)

        for payload in update_course_data["valid"]:
            course_id = payload["course_id"]
            payload.pop("course_id")
            response = await async_client.patch(
                f"{endpoint}/{course_id}", 
                cookies={"refresh_token": refresh_token},
                headers={"Authorization": access_token},
                json=payload
            )
            assert response.status_code == 200

        for payload in update_course_data["invalid"]:
            response_locs = []
            error_code = payload["error_code"]
            payload.pop("error_code")
            course_id = payload["course_id"]
            payload.pop("course_id")
            if error_code == 422:
                validated = payload["locs"]
                payload.pop("locs")
            elif error_code == 404:
                validated = payload["message"]
                payload.pop("message")

            logger.critical(payload)
            response = await async_client.patch(
                f"{endpoint}/{course_id}", 
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
        

        response = await async_client.post(
            post_course_data["endpoint"], 
            cookies={"refresh_token": refresh_token},
            headers={"Authorization": access_token},
            json=post_course_data["valid"][0]
        )
        assert response.status_code == 201
        response_json = response.json()
        course_of_instructor1= response_json["course_id"]

        await sign_out(refresh_token, access_token, async_client)
        
        instructor2_valid_payload = credentials["valid"]["instructor2"]
        refresh_token, access_token = await sign_in(instructor2_valid_payload, async_client)


        payload = update_course_data["valid"][0]
        response = await async_client.patch(
            f"{endpoint}/{course_of_instructor1}", 
            cookies={"refresh_token": refresh_token},
            headers={"Authorization": access_token},
            json=payload
        )
        assert response.status_code == 403