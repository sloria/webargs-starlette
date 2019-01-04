*****************
webargs-starlette
*****************

.. image:: https://badgen.net/pypi/v/webargs-starlette
    :target: https://badge.fury.io/py/webargs-starlette
    :alt: PyPI version

.. image:: https://badgen.net/travis/sloria/webargs-starlette/master
    :target: https://travis-ci.org/sloria/webargs-starlette
    :alt: TravisCI build status

.. image:: https://badgen.net/badge/marshmallow/2,3?list=1
    :target: https://marshmallow.readthedocs.io/en/latest/upgrading.html
    :alt: marshmallow 2/3 compatible

.. image:: https://badgen.net/badge/code%20style/black/000
    :target: https://github.com/ambv/black
    :alt: code style: black


webargs-starlette is a library for declarative request parsing and
validation in `Starlette <https://github.com/encode/starlette>`_,
built on top of `webargs <https://github.com/marshmallow-code/webargs>`_.

.. code-block:: python

    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from webargs import fields
    from webargs_starlette import use_args

    app = Starlette()


    @app.route("/")
    @use_args({"name": fields.Str(missing="world")})
    def index(request, args):
        return JSONResponse({"hello": args["name"]})


    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=5000)

    # curl http://localhost:5000/
    # {"hello": "world"}
    # curl http://localhost:5000/\?name\='steve'
    # {"hello": "steve"}

Install
=======

::

    pip install -U webargs-starlette


Usage
=====

Basic Usage
-----------

Use ``parser.parse`` to parse a Starlette ``Request`` instance with a
dictionary of fields.

.. code-block:: python

    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from webargs import fields
    from webargs_starlette import parser

    app = Starlette()


    @app.route("/")
    async def homepage(request):
        args = {"name": fields.Str(required=True), "greeting": fields.Str(missing="hello")}
        parsed = await parser.parse(args, request)
        greeting = parsed["greeting"]
        name = parsed["name"]
        return JSONResponse({"message": f"{greeting} {name}"})


Decorators
----------

Use the ``use_args`` decorator to inject the parsed args
dictionary into the handler function. The following snippet is equivalent to the
first example.

.. code-block:: python

    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from webargs import fields
    from webargs_starlette import use_args

    app = Starlette()


    @app.route("/")
    @use_args({"name": fields.Str(required=True), "greeting": fields.Str(missing="hello")})
    async def homepage(request, args):
        greeting = args["greeting"]
        name = args["name"]
        return JSONResponse({"message": f"{greeting} {name}"})


The ``use_kwargs`` decorator injects the parsed args as keyword arguments.

.. code-block:: python

    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from webargs import fields
    from webargs_starlette import use_args

    app = Starlette()


    @app.route("/")
    @use_kwargs(
        {"name": fields.Str(required=True), "greeting": fields.Str(missing="hello")}
    )
    async def homepage(request, name, greeting):
        return JSONResponse({"message": f"{greeting} {name}"})


For more information how to use webargs, see the `webargs documentation <https://webargs.readthedocs.io/>`_

Error Handling
--------------

When validation fails, the parser will raise a ``WebargsHTTPException``,
which is the same as Starlette's ``HTTPException`` with the addition of
of the ``messages`` (validation messages), ``headers`` , ``exception`` (underlying exception), and ``schema`` (marshmallow ``Schema``) attributes.

You can use a custom exception handler to return the error messages as
JSON.


.. code-block:: python

    from starlette.responses import JSONResponse
    from webargs_starlette import WebargsHTTPException


    @app.exception_handler(WebargsHTTPException)
    async def http_exception(request, exc):
        return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)


License
=======

MIT licensed. See the `LICENSE <https://github.com/sloria/webargs-starlette/blob/master/LICENSE>`_ file for more details.
