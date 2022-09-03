"""A simple number and datetime addition JSON API.
Uses ``use_args`` and ``use_kwargs`` for parsing requests.

Run the app:

    $ pip install uvicorn
    $ python examples/decorator_example.py

Or, to run with automatic reloading:

    $ uvicorn examples.starlette_example:app --port 5001 --debug

Try the following with httpie (a cURL-like utility, http://httpie.org):

    $ pip install httpie
    $ http GET :5001/
    $ http GET :5001/ name==Ada
    $ http POST :5001/add x=40 y=2
    $ http POST :5001/dateadd value=1973-04-10 addend=63
    $ http POST :5001/dateadd value=2014-10-23 addend=525600 unit=minutes
"""
import datetime as dt

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from webargs import fields, validate
from webargs_starlette import use_args, use_kwargs, WebargsHTTPException

app = Starlette()


@app.route("/")
@use_args({"name": fields.Str(load_default="Friend")}, location="querystring")
async def index(request, args):
    """A welcome page."""
    return JSONResponse({"message": f"Welcome, {args['name']}!"})


@app.route("/add", methods=["POST"])
@use_kwargs(
    {"x": fields.Float(required=True), "y": fields.Float(required=True)},
    location="json",
)
async def add(request, x, y):
    """An addition endpoint."""
    return JSONResponse({"result": x + y})


@app.route("/dateadd", methods=["POST"])
@use_kwargs(
    {
        "value": fields.Date(required=False),
        "addend": fields.Int(required=True, validate=validate.Range(min=1)),
        "unit": fields.Str(
            load_default="days", validate=validate.OneOf(["minutes", "days"])
        ),
    },
    location="json",
)
async def dateadd(request, value, addend, unit):
    """A datetime adder endpoint."""
    value = value or dt.datetime.utcnow()
    if unit == "minutes":
        delta = dt.timedelta(minutes=addend)
    else:
        delta = dt.timedelta(days=addend)
    result = value + delta
    return JSONResponse({"result": result.isoformat()})


# Return errors as JSON
@app.exception_handler(WebargsHTTPException)
async def http_exception(request, exc):
    return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)


if __name__ == "__main__":
    import uvicorn

    app.debug = True
    uvicorn.run(app, host="0.0.0.0", port=5001)
