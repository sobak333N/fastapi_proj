from httpx import AsyncClient
import pytest
import asyncio

from tests.conftest import signup_instructor_data, logger


@pytest.mark.skip(reason="temporary")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_data",
    [
        "signup_student_data",
        "signup_instructor_data",
    ]
)
async def test_signup(test_data, request):
    loop = asyncio.get_running_loop()

    test_data = request.getfixturevalue(test_data)
    # logger.warning(test_data["endpoint"], asyncio.get_running_loop())

    async with AsyncClient(base_url="http://nginx/api/v1") as client:
        # logger.warning(test_data["endpoint"], asyncio.get_running_loop())
        endpoint = test_data["endpoint"]
        for payload in test_data["valid"]:
            response = await client.post(endpoint, json=payload)
            print("="*40)
            print(payload)
            print(response.json())
            response_json = response.json()
            assert response.status_code == 201 
            assert response_json["message"] == "Go to link in email to verify account" 

        for payload in test_data["invalid"]:
            locs = payload["locs"]
            response_locs = []
            payload.pop("locs")

            response = await client.post(endpoint, json=payload)
            print("="*40)
            print(payload)
            print(response.json())
            response_json = response.json()
            assert response.status_code == 422 
            for detail in response_json["detail"]:
                response_locs.append(detail["loc"][1])
            
            response_locs = sorted(response_locs)
            locs = sorted(locs)

            assert response_locs == locs
    # assert loop == asyncio.get_running_loop()

        # logger.warning(test_data["endpoint"], asyncio.get_running_loop())
    # logger.warning(test_data["endpoint"], asyncio.get_running_loop())
