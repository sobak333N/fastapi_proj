from httpx import AsyncClient, Cookies
import pytest
import asyncio
import logging

from tests.conftest import signup_instructor_data, logger
from tests.utils import sign_in, sign_out


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_data",
    [
        ("credentials", "update_category")
    ]
)
async def test_update_category(test_data, request):
    async with AsyncClient(base_url="http://nginx/api/v1", cookies=Cookies()) as async_client:

        credentials = request.getfixturevalue("credentials")
        update_category_data = request.getfixturevalue("update_category")
        endpoint = update_category_data["endpoint"]

        student_valid_payload = credentials["valid"]["student"]
        refresh_token, access_token = await sign_in(student_valid_payload, async_client)

        response = await async_client.patch(
            f"{endpoint}/{update_category_data['valid'][0]['category_id']}", 
            cookies={"refresh_token": refresh_token},
            headers={"Authorization": access_token}
        )
        assert response.status_code == 403

        await sign_out(refresh_token, access_token, async_client)

        admin_valid_payload = credentials["valid"]["admin"]
        refresh_token, access_token = await sign_in(admin_valid_payload, async_client)

        for payload in update_category_data["valid"]:
            category_id = payload['category_id']
            payload.pop('category_id')
            payload = payload["payload"]
            response = await async_client.patch(
                f"{endpoint}/{category_id}", 
                cookies={"refresh_token": refresh_token},
                headers={"Authorization": access_token},
                json=payload
            )
            assert response.status_code == 200

        for payload in update_category_data["invalid"]:
            locs = payload["locs"]
            response_locs = []
            payload.pop("locs")

            category_id = payload['category_id']
            payload.pop('category_id')
            payload = payload["payload"]
            response = await async_client.patch(
                f"{endpoint}/{category_id}", 
                cookies={"refresh_token": refresh_token},
                headers={"Authorization": access_token},
                json=payload
            )
            if "category_id" in locs:
                assert response.status_code == 404
            else:
                assert response.status_code == 422 or response.status_code == 401
                response_json = response.json()
                
                for detail in response_json["detail"]:
                    response_locs.append(detail["loc"][1])
                
                response_locs = sorted(response_locs)
                locs = sorted(locs)
                # logger.critical(response_locs)
                # logger.critical(locs)
                assert response_locs == locs
        
        await sign_out(refresh_token, access_token, async_client)
        
