*****************
webargs-starlette
*****************

.. image:: https://badgen.net/pypi/v/webargs-starlette
    :target: https://badge.fury.io/py/webargs-starlette
    :alt: PyPI version

.. image:: https://dev.azure.com/sloria/sloria/_apis/build/status/sloria.webargs-starlette?branchName=master
    :target: https://dev.azure.com/sloria/sloria/_build/latest?definitionId=11&branchName=master
    :alt: Build status

.. image:: https://badgen.net/badge/marshmallow/2,3?list=1
    :target: https://marshmallow.readthedocs.io/en/latest/upgrading.html
    :alt: marshmallow 2/3 compatible

.. image:: https://badgen.net/badge/code%20style/black/000
    :target: https://github.com/ambv/black
    :alt: code style: black


webargs-starlette is a library for declarative request parsing and
validation with `Starlette <https://github.com/encode/starlette>`_,
built on top of `webargs <https://github.com/marshmallow-code/webargs>`_.

It has all the goodness of `webargs <https://github.com/marshmallow-code/webargs>`_, 
with some extra sugar for type annotations.

.. code-block:: python

    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from webargs_starlette import use_annotations

    app = Starlette()


    @app.route("/")
    @use_annotations(locations=("query",))
    async def index(request, name: str = "World"):
        return JSONResponse({"Hello": name})


    if __name__ == "__main__":
        uvicorn.run(app, port=5000)

    # curl 'http://localhost:5000/'
    # {"Hello": "World"}
    # curl 'http://localhost:5000/?name=Ada'
    # {"Hello": "Ada"}

Install
=======

::

    pip install -U webargs-starlette


Usage
=====

Parser Usage
------------

Use ``parser.parse`` to parse a Starlette ``Request`` with a
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

Use the ``use_args`` decorator to inject the parsed arguments
dictionary into the handler function. The following snippet is equivalent to the
first example.

**Important**: Decorated functions MUST be coroutine functions.

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


The ``use_kwargs`` decorator injects the parsed arguments as keyword arguments.

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


See `decorator_example.py <https://github.com/sloria/webargs-starlette/blob/master/examples/decorator_example.py>`_
for a more complete example of ``use_args`` and ``use_kwargs`` usage.

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


Annotations
-----------

The ``use_annotations`` decorator allows you to parse request objects
using type annotations.


.. code-block:: python

    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from webargs_starlette import use_annotations

    app = Starlette()


    @app.route("/")
    @use_annotations(locations=("query",))
    async def welcome(request, name: str = "Friend"):
        return JSONResponse({"message": f"Welcome, {name}!"})


    # curl 'http://localhost:5000/'.
    # {"message":"Welcome, Friend!"}
    # curl 'http://localhost:5000/?name=Ada'.
    # {"message":"Welcome, Ada!"}

Any annotated argument that doesn't have a default value will be required.
For example, if we remove the default for ``name`` in the above example,
an 422 error response is returned if ``?name`` isn't passed.


.. code-block:: python

    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from webargs_starlette import use_annotations, WebargsHTTPException

    app = Starlette()


    @app.route("/")
    @use_annotations(locations=("query",))
    async def welcome(request, name: str):
        return JSONResponse({"message": f"Welcome, {name}!"})


    @app.exception_handler(WebargsHTTPException)
    async def http_exception(request, exc):
        return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)


    # curl "http://localhost:5000/"
    # {"name":["Missing data for required field."]}

Arguments may also be annotated with ``Field`` instances when you need
more control. For example, you may want to add a validator.

.. code-block:: python

    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from webargs import fields
    from marshmallow import validate
    from webargs_starlette import use_annotations, WebargsHTTPException

    app = Starlette()


    @app.route("/")
    @use_annotations(locations=("query",))
    async def welcome(request, name: fields.Str(validate=validate.Length(min=2))):
        return JSONResponse({"message": f"Welcome, {name}!"})


    @app.exception_handler(WebargsHTTPException)
    async def http_exception(request, exc):
        return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)


    # curl "http://localhost:5000/?name=A"
    # {"name":["Shorter than minimum length 2."]}

``HTTPEndpoint`` classes may also be decorated with ``use_annotations``.

.. code-block:: python

    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.endpoints import HTTPEndpoint
    from webargs_starlette import use_annotations

    app = Starlette()


    @app.route("/")
    @use_annotations(locations=("query",))
    class WelcomeEndpoint(HTTPEndpoint):
        async def get(self, request, name: str = "World"):
            return JSONResponse({"message": f"Welcome, {name}!"})

See `annotation_example.py <https://github.com/sloria/webargs-starlette/blob/master/examples/annotation_example.py>`_
for a more complete example of ``use_annotations`` usage.

More
----

For more information on how to use webargs, see the `webargs documentation <https://webargs.readthedocs.io/>`_.

License
=======

MIT licensed. See the `LICENSE <https://github.com/sloria/webargs-starlette/blob/master/LICENSE>`_ file for more details.
