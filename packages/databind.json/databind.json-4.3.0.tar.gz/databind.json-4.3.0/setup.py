# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['json', 'json.tests']

package_data = \
{'': ['*']}

install_requires = \
['databind.core>=4.3.0,<5.0.0',
 'nr-date>=2.0.0,<3.0.0',
 'typeapi>=1.4.2,<2.0.0',
 'typing-extensions>=3.10.0']

setup_kwargs = {
    'name': 'databind.json',
    'version': '4.3.0',
    'description': 'De-/serialize Python dataclasses to or from JSON payloads. Compatible with Python 3.7 and newer.',
    'long_description': '# databind.json\n\nThe `databind.json` package implements the de-/serialization to or from JSON payloads using\nthe `databind.core` framework.\n\nCheck out the [Documentation][0] for examples.\n\n[0]: https://niklasrosenstein.github.io/python-databind/\n\n## Built-in converters\n\nThe following tables shows which types can be deserialized from / serialize to Python types with the native\nconverters provided by the `databind.json` module:\n\n| Converter name | Types | Description |\n| -------------- | ----- | ----------- |\n| `AnyConverter` | `typing.Any` | Accept any value (useful for arbitrary JSON). |\n| `CollectionConverter` | `typing.Collection[T]`, excl. `str`, `bytes`, `bytearray`, `memoryview` and `typing.Mapping[K, V]` | Converts between native Python collections and JSON arrays. |\n| `DatetimeConverter` | `datetime.date`, `datetime.datetime`, `datetime.time` | Converts between strings and date/time formats, using ISO 8601 time format by default (can be changed with the `databind.core.settings.DateFormat` setting). |\n| `DecimalConverter` | `decimal.Decimal` | Converts between strings (and ints/floats if strict mode is off, strict mode is on by default) and decimals. The precision can be controlled with the `databind.core.settings.Precision` setting. |\n| `EnumConverter` | `enum.Enum`, `enum.IntEnum` | Convert between strings and Python enumerations. The serialized form of `IntEnum` is the integer value, whereas the serialized form of `Enum` is a string (name of the enumeration value). |\n| `MappingConverter` | `typing.Mapping[K, V]` | Converts between Python dicts and JSON objects. (While in theory `K` can be any type, for JSON `K` always needs to be `str`). |\n| `OptionalConverter` | `typing.Optional[T]` | Handles optional fields in a schema. |\n| `PlainDatatypeConverter` | `bytes`, `str`, `int`, `float`, `bool` | Converts between plain datatypes. In non-strict mode (off by default), numeric types will also accept strings as input for the deserialization. |\n| `SchemaConverter` | `dataclasses.dataclass`, `typing.TypedDict` | Converts between Python dataclasses or typed dictionary and JSON objects. |\n| `UnionConverter` | `typing.Union[...]` | Handles union types. Unions in JSON can be expressed in a multitide of ways, e.g. using a discriminator key and flat, keyed or nested structure or "best match". Check out the examples section of the documentation for more information. |\n| `LiteralConverter` | `typing.Literal[...]` | Accepts or rejects a value based on whether it matches one of the values in the literal type hint. |\n\n\nThe following converters are provided for convenience:\n\n| Converter name | Types | Description |\n| -------------- | ----- | ----------- |\n| `StringifyConverter` | n/a | A helper that allows to easily create de/serializers from a "to string" and "from string" function. |\n\nThe following additional types are natively supported by `databind.json` using `StringifyConverter`:\n\n| Types | Description |\n| ----- | ----------- |\n| `uuid.UUID` | Convert between strings and UUIDs. |\n| `pathlib.Path` | Convert between strings and paths. |\n| `pathlib.PurePath` | Convert between strings and paths. |\n| `nr.date.duration` | Deserialize from ISO 8601 duration strings or the object form, serialize to ISO 8601 strings. |\n\n---\n\n<p align="center">Copyright &copy; 2020 &ndash; Niklas Rosenstein</p>\n',
    'author': 'Niklas Rosenstein',
    'author_email': 'rosensteinniklas@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.3,<4.0.0',
}


setup(**setup_kwargs)
