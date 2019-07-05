import re
from setuptools import setup, find_packages

INSTALL_REQUIRES = ["webargs~=5.0", "starlette>=0.9.0"]
EXTRAS_REQUIRE = {
    "tests": ["pytest", "mock", "webtest~=2.0.32", "webtest-asgi~=1.0.1"],
    "examples": ["httpie", "uvicorn"],
    "lint": [
        "mypy==0.711",
        "flake8==3.7.7",
        "flake8-bugbear==19.3.0",
        "pre-commit~=1.17",
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
    with open(fname, "r") as fp:
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
    keywords=("webargs", "starlette", "asgi", "request", "parsing"),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
    ],
    test_suite="tests",
)
