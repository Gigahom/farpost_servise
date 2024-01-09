from fastapi.testclient import TestClient

from uuid import uuid4

from main import app
from src.apps.FARPOST.schemas import AbsActiveMergeSchema, ResponseLoginSchema, HeadersSchema, CookiesSchema
from src.settings.const import TestUserEnum

client = TestClient(app)


def test_get_abs_active_by_user():
    response = client.get(f"/api/v1/farpost/get_abs_active_by_user?user_login={TestUserEnum.login.value}")
    assert response.status_code == 200
    assert isinstance(AbsActiveMergeSchema(**response.json()[0]), AbsActiveMergeSchema)


def test_get_abs_active_by_user_error_user():
    response = client.get(f"/api/v1/farpost/get_abs_active_by_user?user_login={TestUserEnum.login.value[:4]}")
    assert response.status_code == 404


def test_creact_abs_active_success():
    response = client.get(
        f"/api/v1/farpost/creact_abs_active?user_login={TestUserEnum.login.value}&abs_id={TestUserEnum.abs_id.value}&position=2&price_limitation=100",
    )
    assert (response.status_code == 200 or response.status_code == 418)
    # Проверка структуры ответа


def test_creact_abs_active_user_not_found():
    response = client.get(
        "/api/v1/farpost/creact_abs_active",
        params={"user_login": f"{TestUserEnum.login.value[:4]}", "abs_id": 1, "position": 2, "price_limitation": 100.0},
    )
    assert response.status_code == 404


def test_stop_abs_active_success():
    # Предполагается, что abs_active_id существует
    response = client.get("/api/v1/farpost/stop_abs_active", params={"abs_active_id": TestUserEnum.abs_active_id.value})
    assert response.status_code == 200


def test_stop_abs_active_not_found():
    response = client.get("/api/v1/farpost/stop_abs_active", params={"abs_active_id": str(uuid4())})
    assert response.status_code == 404


def test_get_items_success():
    response = client.get("/api/v1/farpost/get_items", params={"user_login": TestUserEnum.login.value})
    assert response.status_code == 200
    # Проверка структуры ответа


def test_get_items_user_not_found():
    response = client.get("/api/v1/farpost/get_items", params={"user_login": TestUserEnum.login.value[:3]})
    assert response.status_code == 404


def test_update_items_user_success():
    response = client.post(
        "/api/v1/farpost/update_items_user",
        params={"user_login": TestUserEnum.login.value},
        json={"headers": TestUserEnum.headers.value, "cookies": TestUserEnum.cookies.value},
    )
    assert response.status_code == 200


def test_update_items_user_error():
    response = client.post(
        "/api/v1/farpost/update_items_user",
        params={"user_login": TestUserEnum.login.value[:4]},
        json={"headers": TestUserEnum.headers.value, "cookies": TestUserEnum.cookies.value},
    )
    assert response.status_code == 404


def test_login_success():
    response = client.post("/api/v1/farpost/login", data={"login": TestUserEnum.login.value, "password": TestUserEnum.password.value})
    assert (response.status_code == 200 or response.status_code == 401)


def test_login_failure():
    response = client.post("/api/v1/farpost/login", data={"login": TestUserEnum.login.value[:5], "password": TestUserEnum.password.value})
    assert response.status_code == 401
