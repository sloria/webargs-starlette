import pytest

from starlette.testclient import TestClient

from examples.decorator_example import app as decorator_app
from examples.annotation_example import app as annotation_app


class TestCommon:
    @pytest.fixture(params=[decorator_app, annotation_app])
    def client(self, request):
        with TestClient(request.param) as client:
            yield client

    def test_index(self, client):
        assert client.get("/").json() == {"message": "Welcome, Friend!"}
        assert client.get("/?name=Ada").json() == {"message": "Welcome, Ada!"}

    def test_add(self, client):
        assert client.post("/add", json={"x": 2, "y": 2}).json() == {"result": 4}

    def test_dateadd(self, client):
        assert client.post(
            "/dateadd", json={"value": "2019-01-03", "addend": 1}
        ).json() == {"result": "2019-01-04"}

    def test_error(self, client):
        res = client.post("/dateadd", json={})
        assert res.status_code == 422
        assert res.json() == {"addend": ["Missing data for required field."]}

        res = client.post("/dateadd", json={"addend": "invalid"})
        assert res.status_code == 422
        assert "addend" in res.json()

        res = client.post("/dateadd", json={"addend": 42, "unit": "invalid"})
        assert res.status_code == 422
        assert "unit" in res.json()


class TestAnnotations:
    @pytest.fixture()
    def client(self):
        with TestClient(annotation_app) as client:
            yield client

    def test_annotation_with_field(self, client):
        assert client.get("/welcome2").json() == {"message": "Welcome, Friend!"}
        assert client.get("/welcome2?name=Ada").json() == {"message": "Welcome, Ada!"}

    def test_param_with_no_default(self, client):
        res = client.get("/welcome3")
        assert res.status_code == 422
        assert res.json() == {"name": ["Missing data for required field."]}
        assert client.get("/welcome3?name=Ada").json() == {"message": "Welcome, Ada!"}
