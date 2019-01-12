import typing

import pytest
from starlette.requests import Request
from starlette.responses import Response
from marshmallow import fields
from webargs.core import MARSHMALLOW_VERSION_INFO

from webargs_starlette.annotations import annotations2schema, DEFAULT_TYPE_MAPPING


def test_annotations2schema():
    @typing.no_type_check
    def func(
        req: Request, x: int, y: fields.Int(missing=42), z: str = "zee"
    ) -> Response:
        return Response

    schema = annotations2schema(func)()
    x_field = schema.fields["x"]
    assert isinstance(x_field, fields.Int)
    assert x_field.required is True

    y_field = schema.fields["y"]
    assert isinstance(y_field, fields.Int)
    assert y_field.missing == 42

    z_field = schema.fields["z"]
    assert isinstance(z_field, fields.Str)
    assert z_field.required is False
    assert z_field.missing == "zee"

    assert "req" not in schema.fields


def test_annotations2schema_handles_collection_types():
    def func(x: dict, y: list):
        pass

    schema = annotations2schema(func)()
    assert isinstance(schema.fields["x"], fields.Dict)
    assert isinstance(schema.fields["y"], fields.List)


def test_annotations2schema_handles_generic_collection_types():
    def func(x: typing.Mapping, y: typing.Iterable, z: typing.List):
        pass

    schema = annotations2schema(func)()
    assert isinstance(schema.fields["x"], fields.Dict)
    assert isinstance(schema.fields["y"], fields.List)
    assert isinstance(schema.fields["z"], fields.List)


def test_annotations2schema_handles_collection_types_with_parameters():
    def func(x: typing.Mapping[str, int], y: typing.Iterable[str], z: typing.List[int]):
        pass

    schema = annotations2schema(func)()
    x_field = schema.fields["x"]
    y_field = schema.fields["y"]
    z_field = schema.fields["z"]
    assert isinstance(x_field, fields.Dict)
    if MARSHMALLOW_VERSION_INFO[0] >= 3:
        assert isinstance(x_field.key_container, fields.Str)
        assert isinstance(x_field.value_container, fields.Int)
    assert isinstance(y_field, fields.List)
    assert isinstance(y_field.container, fields.Str)
    assert isinstance(z_field, fields.List)
    assert isinstance(z_field.container, fields.Int)


def test_annotation2schema_type_not_in_mapping():
    class MyType:
        pass

    def func(x: int, y: MyType):
        pass

    with pytest.raises(TypeError):
        annotations2schema(func)

    type_mapping = DEFAULT_TYPE_MAPPING.copy()
    type_mapping[MyType] = fields.Int

    schema = annotations2schema(func, type_mapping=type_mapping)()
    y_field = schema.fields["y"]
    assert isinstance(y_field, fields.Int)
