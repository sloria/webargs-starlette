from starlette.applications import Starlette
from starlette.responses import JSONResponse as J
from starlette.exceptions import HTTPException

import marshmallow as ma
from webargs import fields
from webargs_starlette import parser, use_args, use_kwargs

from webargs.core import MARSHMALLOW_VERSION_INFO

app = Starlette()
app.debug = True

hello_args = {"name": fields.Str(missing="World", validate=lambda n: len(n) >= 3)}
hello_multiple = {"name": fields.List(fields.Str())}


class HelloSchema(ma.Schema):
    name = fields.Str(missing="World", validate=lambda n: len(n) >= 3)


strict_kwargs = {"strict": True} if MARSHMALLOW_VERSION_INFO[0] < 3 else {}
hello_many_schema = HelloSchema(many=True, **strict_kwargs)


@app.route("/echo", methods=["GET", "POST"])
async def echo(request):
    return J(await parser.parse(hello_args, request))


@app.route("/echo_query")
async def echo_query(request):
    parsed = await parser.parse(hello_args, request, locations=("query",))
    return J(parsed)


@app.route("/echo_use_args", methods=["GET", "POST"])
@use_args(hello_args)
async def echo_use_args(request, args):
    return J(args)


@app.route("/echo_use_args_validated", methods=["GET", "POST"])
@use_args({"value": fields.Int()}, validate=lambda args: args["value"] > 42)
async def echo_use_args_validated(request, args):
    return J(args)


@app.route("/echo_use_kwargs", methods=["GET", "POST"])
@use_kwargs(hello_args)
async def echo_use_kwargs(request, name):
    return J({"name": name})


@app.route("/echo_multi", methods=["GET", "POST"])
async def echo_multi(request):
    result = await parser.parse(hello_multiple, request)
    return J(result)


@app.route("/echo_many_schema", methods=["GET", "POST"])
async def many_nested(request):
    arguments = await parser.parse(hello_many_schema, request, locations=("json",))
    return J(arguments)


@app.route("/echo_use_args_with_path_param/{name}")
@use_args({"value": fields.Int()})
async def echo_use_args_with_path(request, args):
    return J(args)


@app.route("/echo_use_kwargs_with_path_param/{name}")
@use_kwargs({"value": fields.Int()})
async def echo_use_kwargs_with_path(request, value):
    return J({"value": value})


@app.route("/error", methods=["GET", "POST"])
async def error(request):
    def always_fail(value):
        raise ma.ValidationError("something went wrong")

    args = {"text": fields.Str(validate=always_fail)}
    return J(await parser.parse(args, request))


@app.route("/echo_headers")
async def echo_headers(request):
    return J(await parser.parse(hello_args, request, locations=("headers",)))


@app.route("/echo_cookie")
async def echo_cookie(request):
    return J(await parser.parse(hello_args, request, locations=("cookies",)))


@app.route("/echo_nested", "POST")
async def echo_nested(request):
    args = {"name": fields.Nested({"first": fields.Str(), "last": fields.Str()})}
    parsed = await parser.parse(args, request)
    return J(parsed)


@app.route("/echo_nested_many", "POST")
async def echo_nested_many(request):
    args = {
        "users": fields.Nested({"id": fields.Int(), "name": fields.Str()}, many=True)
    }
    parsed = await parser.parse(args, request)
    return J(parsed)


@app.route("/echo_path_param/{path_param}")
async def echo_path_param(request):
    parsed = await parser.parse(
        {"path_param": fields.Int()}, request, locations=("path_params",)
    )
    return J(parsed)


@app.exception_handler(HTTPException)
async def http_exception(request, exc):
    messages = exc.data["messages"]
    return J(messages, status_code=exc.status_code)
