import re
from setuptools import setup, find_packages

INSTALL_REQUIRES = ["webargs~=8.0", "starlette>=0.21.0", "marshmallow~=3.0"]
EXTRAS_REQUIRE = {
    "tests": ["pytest", "mock", "webtest~=2.0.32", "webtest-asgi~=1.1.0"],
    "examples": ["httpie", "uvicorn"],
    "lint": [
        "mypy==0.971",
        "flake8==5.0.4",
        "flake8-bugbear==22.8.23",
        "pre-commit~=2.20",
    ],
}
EXTRAS_REQUIRE["dev"] = (
    EXTRAS_REQUIRE["tests"]
    + EXTRAS_REQUIRE["lint"]
    + EXTRAS_REQUIRE["examples"]
    + ["tox"]
)


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ""
    with open(fname) as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError("Cannot find version information")
    return version


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name="webargs-starlette",
    version=find_version("webargs_starlette/__init__.py"),
    description="Declarative request parsing and validation for Starlette with webargs",
    long_description=read("README.rst"),
    author="Steven Loria",
    author_email="sloria1@gmail.com",
    url="https://github.com/sloria/webargs-starlette",
    packages=find_packages(exclude=("test*", "examples")),
    package_data={"webargs_starlette": ["py.typed"]},
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    license="MIT",
    zip_safe=False,
    keywords=["webargs", "starlette", "asgi", "request", "parsing"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
    ],
    test_suite="tests",
)
