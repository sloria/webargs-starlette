from starlette.applications import Starlette
from starlette.responses import JSONResponse as J
from starlette.endpoints import HTTPEndpoint
import marshmallow as ma
from webargs import fields
from webargs_starlette import (
    parser,
    use_args,
    use_kwargs,
    use_annotations,
    WebargsHTTPException,
)

app = Starlette()
app.debug = True


class HelloSchema(ma.Schema):
    name = fields.Str(load_default="World", validate=lambda n: len(n) >= 3)


hello_args = {"name": fields.Str(load_default="World", validate=lambda n: len(n) >= 3)}
hello_multiple = {"name": fields.List(fields.Str())}
hello_exclude_schema = HelloSchema(unknown=ma.EXCLUDE)
hello_many_schema = HelloSchema(many=True)


@app.route("/echo", methods=["GET"])
async def echo(request):
    return J(await parser.parse(hello_args, request, location="query"))


@app.route("/echo_query")
async def echo_query(request):
    parsed = await parser.parse(hello_args, request, location="query")
    return J(parsed)


@app.route("/echo_json", methods=["POST"])
async def echo_json(request):
    parsed = await parser.parse(hello_args, request, location="json")
    return J(parsed)


@app.route("/echo_form", methods=["POST"])
async def echo_form(request):
    parsed = await parser.parse(hello_args, request, location="form")
    return J(parsed)


@app.route("/echo_json_or_form", methods=["POST"])
async def echo_json_or_form(request):
    parsed = await parser.parse(hello_args, request, location="json_or_form")
    return J(parsed)


@app.route("/echo_ignoring_extra_data", methods=["POST"])
async def echo_json_ignore_extra_data(request):
    parsed = await parser.parse(hello_exclude_schema, request)
    return J(parsed)


@app.route("/echo_use_args", methods=["GET"])
@use_args(hello_args, location="query")
async def echo_use_args(request, args):
    return J(args)


@app.route("/echo_use_args_validated", methods=["POST"])
@use_args(
    {"value": fields.Int()}, validate=lambda args: args["value"] > 42, location="form"
)
async def echo_use_args_validated(request, args):
    return J(args)


@app.route("/echo_use_kwargs", methods=["GET"])
@use_kwargs(hello_args, location="query")
async def echo_use_kwargs(request, name):
    return J({"name": name})


@app.route("/echo_multi", methods=["GET"])
async def echo_multi(request):
    result = await parser.parse(hello_multiple, request, location="query")
    return J(result)


@app.route("/echo_multi_form", methods=["POST"])
async def echo_multi_form(request):
    result = await parser.parse(hello_multiple, request, location="form")
    return J(result)


@app.route("/echo_multi_json", methods=["POST"])
async def echo_multi_json(request):
    result = await parser.parse(hello_multiple, request, location="json")
    return J(result)


@app.route("/echo_many_schema", methods=["GET", "POST"])
async def many_nested(request):
    arguments = await parser.parse(hello_many_schema, request, location="json")
    return J(arguments)


@app.route("/echo_use_args_with_path_param/{name}")
@use_args({"value": fields.Int()}, location="query")
async def echo_use_args_with_path(request, args):
    return J(args)


@app.route("/echo_use_kwargs_with_path_param/{name}")
@use_kwargs({"value": fields.Int()}, location="query")
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
    # the "exclude schema" must be used in this case because WSGI headers may
    # be populated with many fields not sent by the caller
    return J(await parser.parse(hello_exclude_schema, request, location="headers"))


@app.route("/echo_cookie")
async def echo_cookie(request):
    return J(await parser.parse(hello_args, request, location="cookies"))


@app.route("/echo_nested", methods=["POST"])
async def echo_nested(request):
    args = {"name": fields.Nested({"first": fields.Str(), "last": fields.Str()})}
    parsed = await parser.parse(args, request)
    return J(parsed)


@app.route("/echo_nested_many", methods=["POST"])
async def echo_nested_many(request):
    args = {
        "users": fields.Nested({"id": fields.Int(), "name": fields.Str()}, many=True)
    }
    parsed = await parser.parse(args, request)
    return J(parsed)


@app.route("/echo_path_param/{path_param}")
async def echo_path_param(request):
    parsed = await parser.parse(
        {"path_param": fields.Int()}, request, location="path_params"
    )
    return J(parsed)


@app.route("/echo_endpoint/")
class EchoEndpoint(HTTPEndpoint):
    @use_args(hello_args, location="query")
    async def get(self, request, args):
        return J(args)


@app.route("/echo_endpoint_annotations/")
class EchoEndpointAnnotations(HTTPEndpoint):
    @use_annotations(location="query")
    async def get(self, request, name: str = "World"):
        return J({"name": name})


@app.exception_handler(WebargsHTTPException)
async def http_exception(request, exc):
    return J(exc.messages, status_code=exc.status_code, headers=exc.headers)
