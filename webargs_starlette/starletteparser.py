import typing
import json

from marshmallow import Schema, ValidationError
from marshmallow.fields import Field
from starlette.requests import Request
from starlette.exceptions import HTTPException
from webargs.asyncparser import AsyncParser
from webargs import core


def abort(
    http_status_code: int, exc: Exception = None, detail: str = None, **kwargs
) -> None:
    """Raise a HTTPException for the given http_status_code. Attach any keyword
    arguments to the exception for later processing.
    """
    exception = HTTPException(http_status_code, detail=detail)
    exception.data = kwargs
    exception.exc = exc
    raise exception


def is_json_request(req: Request) -> bool:
    content_type = req.headers.get("content-type")
    return core.is_json(content_type)


class StarletteParser(AsyncParser):
    __location_map__ = dict(
        path_params="parse_path_params", **core.Parser.__location_map__
    )

    def parse_path_params(self, req: Request, name: str, field: Field) -> typing.Any:
        return core.get_value(req.path_params, name, field)

    def parse_querystring(self, req: Request, name: str, field: Field) -> typing.Any:
        """Pull a querystring value from the request."""
        return core.get_value(req.query_params, name, field)

    def parse_headers(self, req: Request, name: str, field: Field) -> typing.Any:
        """Pull a value from the header data."""
        return core.get_value(req.headers, name, field)

    def parse_cookies(self, req: Request, name: str, field: Field):
        """Pull a value from the cookiejar."""
        return core.get_value(req.cookies, name, field)

    async def parse_json(self, req: Request, name: str, field: Field) -> typing.Any:
        """Pull a json value from the request."""
        json_data = self._cache.get("json")
        if json_data is None:
            if not is_json_request(req):
                return core.missing
            try:
                json_data = await req.json()
            except json.JSONDecodeError as e:
                if e.doc == "":
                    return core.missing
                else:
                    return self.handle_invalid_json_error(e, req)
            self._cache["json"] = json_data
        return core.get_value(json_data, name, field, allow_many_nested=True)

    def handle_invalid_json_error(
        self, error: json.JSONDecodeError, req: Request, *args, **kwargs
    ) -> None:
        abort(400, exc=error, messages={"json": ["Invalid JSON body."]})

    async def parse_form(self, req, name, field) -> typing.Any:
        """Pull a form value from the request."""
        post_data = self._cache.get("form")
        if post_data is None:
            self._cache["form"] = await req.form()
        return core.get_value(self._cache["form"], name, field)

    def get_request_from_view_args(self, view, args, kwargs) -> Request:
        """Get request object from a handler function or method. Used internally by
        ``use_args`` and ``use_kwargs``.
        """
        req = None
        for arg in args:
            if isinstance(arg, Request):
                req = arg
                break
        assert isinstance(req, Request), "Request argument not found for handler"
        return req

    def handle_error(
        self,
        error: ValidationError,
        req: Request,
        schema: Schema,
        error_status_code: typing.Union[int, None],
        error_headers: typing.Union[dict, None],
    ) -> None:
        """Handles errors during parsing. Aborts the current HTTP request and
        responds with a 422 error.
        """
        status_code = error_status_code or self.DEFAULT_VALIDATION_STATUS
        abort(
            status_code,
            exc=error,
            messages=error.messages,
            schema=schema,
            headers=error_headers,
        )


parser = StarletteParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
