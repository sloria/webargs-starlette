import pytest

from starlette.testclient import TestClient

from examples.starlette_example import app


@pytest.fixture()
def client():
    return TestClient(app)


def test_index(client):
    assert client.get("/").json() == {"message": "Welcome, Friend!"}
    assert client.get("/?name=Ada").json() == {"message": "Welcome, Ada!"}


def test_add(client):
    assert client.post("/add", json={"x": 2, "y": 2}).json() == {"result": 4}


def test_dateadd(client):
    assert client.post(
        "/dateadd", json={"value": "2019-01-03", "addend": 1}
    ).json() == {"result": "2019-01-04"}


def test_error(client):
    res = client.post("/dateadd", json={})
    assert res.status_code == 422
    assert res.json() == {"addend": ["Missing data for required field."]}

    res = client.post("/dateadd", json={"addend": "invalid"})
    assert res.status_code == 422
    assert "addend" in res.json()

    res = client.post("/dateadd", json={"addend": 42, "unit": "invalid"})
    assert res.status_code == 422
    assert "unit" in res.json()
