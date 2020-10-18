import pytest
import webtest_asgi

from webargs.testing import CommonTestCase

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

    @pytest.mark.parametrize(
        "url",
        ["/echo_endpoint/", "/echo_endpoint_annotations/"],
    )
    def test_endpoint_method(self, testapp, url):
        assert testapp.get(url).json == {"name": "World"}
        assert testapp.get(url + "?name=Ada").json == {"name": "Ada"}
