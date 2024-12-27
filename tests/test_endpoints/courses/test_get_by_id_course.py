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
        ("credentials", "get_course_by_id")
    ]
)
async def test_get_by_id_course(test_data, request):
    async with AsyncClient(base_url="http://nginx/api/v1", cookies=Cookies()) as async_client:
        credentials = request.getfixturevalue("credentials")
        course_data = await request.getfixturevalue("get_course_by_id")
        logger.critical(course_data)
        logger.critical("END")
        # endpoint = post_course_data["endpoint"]


        res = await session.execute(text("SELECT * FROM users"))
        res = res.scalars().all()
        logger.critical(f"{res=}")


        student_valid_payload = credentials["valid"]["student3"]
        await asyncio.sleep(2)
        refresh_token, access_token = await sign_in(student_valid_payload, async_client)

        # response = await async_client.post(
        #     endpoint, 
        #     cookies={"refresh_token": refresh_token},
        #     headers={"Authorization": access_token}
        # )
        # assert response.status_code == 403

        # await sign_out(refresh_token, access_token, async_client)

        # instructor1_valid_payload = credentials["valid"]["instructor1"]
        # refresh_token, access_token = await sign_in(instructor1_valid_payload, async_client)

        # for payload in post_course_data["valid"]:
        #     response = await async_client.post(
        #         endpoint, 
        #         cookies={"refresh_token": refresh_token},
        #         headers={"Authorization": access_token},
        #         json=payload
        #     )
        #     assert response.status_code == 201
