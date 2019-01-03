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
validation in `Starlette <https://github.com/encode/starlette>`_
applications, using the `webargs <https://github.com/marshmallow-code/webargs>`_ library.

.. code-block:: python

    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from webargs import fields
    from webargs_starlette import use_args

    app = Starlette()

    hello_args = {"name": fields.Str(missing="world")}


    @app.route("/")
    @use_args(hello_args)
    def index(request, args):
        return JSONResponse({"hello": args["name"]})


    if __name__ == "__main__":
        uvicorn.run(app, host='0.0.0.0', port=5000)

    # curl http://localhost:5000/
    # {"hello": "world"}
    # curl http://localhost:5000/\?name\='steve'
    # {"hello": "steve"}

Install
=======

::

    pip install -U webargs-starlette


License
=======

MIT licensed. See the `LICENSE <https://github.com/sloria/webargs-starlette/blob/master/LICENSE>`_ file for more details.
