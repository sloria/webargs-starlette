*********
Changelog
*********

2.0.0 (2020-05-05)
------------------

Features:

* *Backwards-incompatible*: Support webargs 6.x. webargs<6 is no longer supported.
* Tested against Python 3.8.

Other changes:

* *Backwards-incompatible*: Drop support for marshmallow 2.x. Only marshmallow>=3 is supported.

1.2.1 (2020-05-04)
------------------

Bug fixes:

* Handle ``JSONDecodeError`` when parsing JSON.

1.2.0 (2019-07-05)
------------------

Features:

* Export type annotations.

1.1.0 (2019-01-13)
------------------

Features:

* ``use_annotations`` supports more types in the ``typing`` module, as
  well as ``dict`` and ``list``.
* ``use_annotations`` supports ``typing.Optional``.
* Improve type annotations.

1.0.0 (2019-01-04)
------------------

* First release.
