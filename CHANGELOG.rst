*********
Changelog
*********

2.1.0 (2022-12-04)
------------------

Features:

* Tested against Python 3.9, 3.10, and 3.11.

Bug fixes:

* Various typing fixes.

Other changes:

* Drop support for Python 3.6.

Thanks `@DmitryBurnaev <https://github.com/DmitryBurnaev>`_ for the PR for these changes.

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
