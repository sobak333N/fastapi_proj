from httpx import AsyncClient
import pytest

from app.main import app
from tests.conftest import signup_student_data


@pytest.mark.asyncio
async def test_register_user(signup_student_data):
    async with AsyncClient(app=app, base_url="http://nginx/api/v1") as client:
        for payload in signup_student_data["valid"]:
            # response = await client.post("/auth/signup/student", json={})
            response = await client.post("/auth/signup/student", json=payload)
            print(payload)
            print("="*40)
            print(response.json())
            response_json = response.json()
            assert response.status_code == 201 
            assert response_json["message"] == "Go to link in email to verify account" 

        for payload in signup_student_data["invalid"]:
            # response = await client.post("/auth/signup/student", json={})
            response = await client.post("/auth/signup/student", json=payload)
            print(payload)
            print("="*40)
            print(response.json())
            response_json = response.json()
            assert response.status_code == 201 
            assert response_json["message"] == "Go! to link in email to verify account" 

            # assert response.json()["email"] == payload["email"]

    # assert response.status_code == 201  # Успешное создание пользователя
    # assert response.json()["username"] == "test_user"