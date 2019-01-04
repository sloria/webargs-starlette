"""A simple number and datetime addition JSON API.
Uses ``use_annotations`` for parsing requests.

Run the app:

    $ pip install uvicorn
    $ python examples/annotation_example.py

Or, to run with automatic reloading:

    $ uvicorn examples.annotation_example:app --port 5001 --debug

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
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from webargs import fields, validate
from webargs_starlette import use_annotations, WebargsHTTPException

app = Starlette()


@app.route("/")
@use_annotations(locations=("query",))
async def welcome(request: Request, name: str = "Friend") -> Response:
    """A welcome page."""
    return JSONResponse({"message": f"Welcome, {name}!"})


@app.route("/welcome2")
@use_annotations(locations=("query",))
async def welcome2(
    request: Request, name: fields.Str(missing="Friend", location="querystring")
) -> Response:
    """A welcome page, using a field annotation."""
    return JSONResponse({"message": f"Welcome, {name}!"})


@app.route("/welcome3")
@use_annotations(locations=("query",))
async def welcome_no_default(request: Request, name: str) -> Response:
    """A welcome page with no default name. If "name" isn't passed in the querystring,
    an error response will be returned.
    """
    return JSONResponse({"message": f"Welcome, {name}!"})


@app.route("/add", "POST")
@use_annotations(locations=("json",))
async def add(request: Request, x: float, y: float) -> Response:
    """An addition endpoint."""
    return JSONResponse({"result": x + y})


@app.route("/dateadd", "POST")
@use_annotations(locations=("json",))
async def dateadd(
    request: Request,
    addend: fields.Int(required=True, validate=validate.Range(min=1)),
    unit: fields.Str(missing="days", validate=validate.OneOf(["minutes", "days"])),
    value: dt.date = None,
) -> Response:
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
async def http_exception(request: Request, exc: WebargsHTTPException) -> Response:
    return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)


if __name__ == "__main__":
    app.debug = True
    uvicorn.run(app, host="0.0.0.0", port=5001)
