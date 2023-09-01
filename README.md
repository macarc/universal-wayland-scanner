# Documentation

Universal Wayland Scanner aims to provide an easy-to-use interface for generating Wayland bindings (ala `wayland-scanner`) for many languages.

## Status

Still very much experimental. Doesn't process version data yet.

## Usage

The entire code is contained in `scanner.py`. You run at the command line:

```
> python scanner.py < [protocol-specification.xml]
> # E.g.
> python scanner.py < /usr/share/wayland/wayland.xml
```

Which just pretty-prints the result of the parse.

To use as a library:

```
def parse_string(string: String) -> Specification
def parse_stdin() -> Specification
```

`parse_stdin()` is a convenience method over `parse_string(string)`.

You can then write code that deals with these classes, instead of XML. An example is given in `c.py`.


## Classes

```python
class Specification:
  name: Name
  copyright: string | None
  interfaces: List[Interface]
```

```python
class Interface:
  name: Name
  description: Description | None
  enums: List[Enum]
  events: List[Event]
  requests: List[Request]
```

```python
class EnumEntry:
  name: Name
  value: string
  summary: string | None

class Enum:
  name: Name
  description: Description | None
  entries: List[EnumEntry]
```

```python
class Event:
  name: Name
  description: Description | None
  args: List[Arg]
```

```python
class Request:
  name: Name
  description: Description | None
  is_destructor: Boolean
  args: ArgList

class ArgList::
  def return_type() -> Arg | None
  def parameters() -> List[Arg]

class Arg:
  name: Name
  type: wayland_type
  interface: Name | None
  nullable: Boolean
  summary: string | None

type wayland_type = "uint" | "int" | "fixed" | "string" | "object" | "array" | "fd"
```

If the arg's type is `object` or `new_id`, then `interface` may contain a `string` with the name of the interface.

```python
class Description:
  text: string
  summary: string | None
```
```python
class Name:
  # snake_case
  def snake() -> string
  # SCREAMING_CASE
  def screaming() -> string
  # PascalCase
  def pascal() -> string
  # camelCase
  def camel() -> string
  # text case
  def text() -> string
  # name1 + name2 adds a separator between the names
  # (e.g. a _ when accessed with .snake())
  def __add__(other: Name | string) -> Name
```

## Errors

```
class ScannerError
```

Raised when the parser hits an unknown item in the tree (i.e. the XML file is not valid).

```
class UnknownTypeError
```

Raised when an argument to a request or event is not a valid (known) type (i.e. is not a `wayland_type` as defined below).

