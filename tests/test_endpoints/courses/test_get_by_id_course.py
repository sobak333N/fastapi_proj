from os import eventfd
from typing import Literal
from httpx import AsyncClient, Cookies
import pytest
import asyncio
import logging

from tests.conftest import signup_instructor_data, logger
from tests.utils import sign_in, sign_out, private_info



@pytest.mark.anyio
@pytest.mark.parametrize(
    "test_data",
    [
        ("credentials", "get_course_by_id")
    ]
)
async def test_get_by_id_course(test_data: Literal['credentials'], credentials, get_course_by_id):
    async with AsyncClient(base_url="http://nginx/api/v1", cookies=Cookies()) as async_client:
        logger.critical(get_course_by_id)
        logger.critical("END")

        get_course_by_id_data = get_course_by_id
        endpoint = get_course_by_id_data["endpoint"]
        course_id = get_course_by_id_data["course_id"]
        endpoint += str(course_id)

        response = await async_client.get(
            endpoint
        )
        assert response.status_code == 200
        response_json = response.json()
        assert response_json.get("private_info", None) is None


        await private_info(
            credentials["valid"]["instructor1"], endpoint, True, async_client
        )
        await private_info(
            credentials["valid"]["instructor2"], endpoint, False, async_client
        )
        await private_info(
            credentials["valid"]["student1"], endpoint, False, async_client
        )
        await private_info(
            credentials["valid"]["student2"], endpoint, True, async_client
        )
        await private_info(
            credentials["valid"]["student3"], endpoint, False, async_client
        )
