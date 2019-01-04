"""A simple number and datetime addition JSON API.
Run the app:

    $ python examples/starlette_example.py

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
import uvicorn
import datetime as dt

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from webargs import fields, validate
from webargs_starlette import use_args, use_kwargs, WebargsHTTPException

app = Starlette()


@app.route("/")
@use_args({"name": fields.Str(missing="Friend")})
async def index(request, args):
    """A welcome page."""
    return JSONResponse({"message": f"Welcome, {args['name']}!"})


@app.route("/add", "POST")
@use_kwargs({"x": fields.Float(required=True), "y": fields.Float(required=True)})
async def add(request, x, y):
    """An addition endpoint."""
    return JSONResponse({"result": x + y})


@app.route("/dateadd", "POST")
@use_kwargs(
    {
        "value": fields.Date(required=False),
        "addend": fields.Int(required=True, validate=validate.Range(min=1)),
        "unit": fields.Str(
            missing="days", validate=validate.OneOf(["minutes", "days"])
        ),
    }
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
    app.debug = True
    uvicorn.run(app, host="0.0.0.0", port=5001)