import typing
import functools
import json

from marshmallow import Schema, ValidationError
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.endpoints import HTTPEndpoint
from webargs.asyncparser import AsyncParser
from webargs import core
from webargs.multidictproxy import MultiDictProxy
from .annotations import TypeMapping, DEFAULT_TYPE_MAPPING, annotations2schema

HTTP_METHOD_NAMES: typing.List[str] = [
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
    "trace",
]


class WebargsHTTPException(HTTPException):
    """Same as `starlette.exceptions.HTTPException` but stores validation
    messages, the underlying exception, the `marshmallow.Schema` used to parse the request,  headers.
    """

    def __init__(
        self,
        status_code: int,
        detail: typing.Optional[str] = None,
        messages: typing.Optional[dict] = None,
        exception: typing.Optional[Exception] = None,
        headers: typing.Optional[dict] = None,
        schema: typing.Optional[Schema] = None,
    ) -> None:
        super().__init__(status_code, detail)
        self.messages = messages
        self.exception = exception
        self.headers = headers
        self.schema = schema


def is_json_request(req: Request) -> bool:
    content_type = req.headers.get("content-type")
    return core.is_json(content_type)


class StarletteParser(AsyncParser):
    """Starlette request argument parser."""

    TYPE_MAPPING: TypeMapping = DEFAULT_TYPE_MAPPING

    __location_map__: typing.Dict[str, typing.Union[str, typing.Callable]] = dict(
        path_params="load_path_params", **core.Parser.__location_map__
    )

    def load_path_params(self, req: Request, schema: Schema) -> typing.Any:
        """Return the request's ``path_params`` or ``missing`` if there are none."""
        return req.path_params or core.missing

    def load_querystring(self, req: Request, schema: Schema) -> MultiDictProxy:
        """Return query params from the request as a MultiDictProxy."""
        return MultiDictProxy(req.query_params, schema)

    def load_headers(self, req: Request, schema: Schema) -> MultiDictProxy:
        """Return headers from the request as a MultiDictProxy."""
        return MultiDictProxy(req.headers, schema)

    def load_cookies(self, req: Request, schema: Schema):
        """Return cookies from the request."""
        return req.cookies

    async def load_json(self, req: Request, schema: Schema) -> typing.Dict:
        """Return a parsed json payload from the request."""
        if not is_json_request(req):
            return core.missing
        try:
            json_data = await req.json()
        except json.JSONDecodeError as exc:
            if exc.doc == "":
                return core.missing
            else:
                return self._handle_invalid_json_error(exc, req)
        except UnicodeDecodeError as exc:
            return self._handle_invalid_json_error(exc, req)
        return json_data

    async def load_form(self, req: Request, schema: Schema) -> MultiDictProxy:
        """Return form values from the request as a MultiDictProxy."""
        post_data = await req.form()
        return MultiDictProxy(post_data, schema)

    async def load_json_or_form(
        self, req: Request, schema: Schema
    ) -> typing.Union[typing.Dict, MultiDictProxy]:
        data = await self.load_json(req, schema)
        if data is not core.missing:
            return data
        return await self.load_form(req, schema)

    def _handle_invalid_json_error(
        self, error: Exception, req: Request, *args, **kwargs
    ) -> typing.NoReturn:
        raise WebargsHTTPException(
            400, exception=error, messages={"json": ["Invalid JSON body."]}
        )

    def get_request_from_view_args(
        self, view: typing.Callable, args: tuple, kwargs: dict
    ) -> Request:
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
    ) -> typing.NoReturn:
        """Handles errors during parsing. Aborts the current HTTP request and
        responds with a 422 error.
        """
        status_code = error_status_code or self.DEFAULT_VALIDATION_STATUS
        raise WebargsHTTPException(
            status_code,
            exception=error,
            messages=error.messages,
            schema=schema,
            headers=error_headers,
        )

    def use_annotations(
        self,
        fn: typing.Union[typing.Callable, HTTPEndpoint, None] = None,
        *,
        type_mapping: TypeMapping = None,
        **kwargs,
    ) -> typing.Union[typing.Callable[..., typing.Callable], HTTPEndpoint]:
        # Allow using this as either a decorator or a decorator factory.
        if fn is None:
            return functools.partial(
                use_annotations, type_mapping=type_mapping, **kwargs
            )
        type_mapping = type_mapping or self.TYPE_MAPPING

        def decorator(func: typing.Callable) -> typing.Callable:
            schema = annotations2schema(func, type_mapping=type_mapping)

            @functools.wraps(func)
            async def wrapper(*a, **kw):
                request = self.get_request_from_view_args(func, a, kw)
                parsed = await self.parse(schema, request, **kwargs)
                kw.update(parsed)
                return await func(*a, **kw)

            return wrapper

        if isinstance(fn, type) and issubclass(fn, HTTPEndpoint):
            endpoint = fn
            # Decorate each HTTP-mapped method
            for each in HTTP_METHOD_NAMES:
                if hasattr(endpoint, each):
                    handler = getattr(endpoint, each)
                    setattr(endpoint, each, decorator(handler))
            return endpoint
        else:
            return decorator(fn)


parser = StarletteParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
use_annotations = parser.use_annotations
