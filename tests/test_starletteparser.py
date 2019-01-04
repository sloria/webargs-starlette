import pytest
import webtest_asgi

from webargs.testing import CommonTestCase
from webargs import fields
from webargs_starlette.starletteparser import annotations2schema

from .app import app


class TestStarletteParser(CommonTestCase):
    def create_app(self):
        return app

    def create_testapp(self, app):
        return webtest_asgi.TestApp(app)

    @pytest.mark.skip(reason="form keys with multiple values not supported")
    def test_parse_form_multiple(self):
        pass

    @pytest.mark.skip(reason="files location not supported")
    def test_parse_files(self):
        pass

    def test_parsing_path_params(self, testapp):
        res = testapp.get("/echo_path_param/42")
        assert res.json == {"path_param": 42}


def test_annotations2schema():
    def func(x: int, y: fields.Int(missing=42), z: str = "zee"):
        pass

    schema = annotations2schema(func)()
    x_field = schema.fields["x"]
    assert isinstance(x_field, fields.Int)
    assert x_field.required is True

    y_field = schema.fields["y"]
    assert isinstance(y_field, fields.Int)
    assert y_field.missing == 42

    z_field = schema.fields["z"]
    assert isinstance(z_field, fields.Str)
    assert z_field.required is False
    assert z_field.missing == "zee"
