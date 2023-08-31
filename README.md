# Documentation

Universal Wayland Scanner aims to provide an easy-to-use interface for generating Wayland bindings for many languages.

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
def parse_string(string: String) -> WaylandSpecification
def parse_stdin() -> WaylandSpecification
```

`parse_stdin()` is a convenience method over `parse_string(string)`.


## Classes

```
class WaylandSpecification:
  name: string
  copyright: string | None
  interfaces: List[WaylandInterface]
```

```
class WaylandInterface:
  name: string
  description: string | None
  enums: List[WaylandEnum]
  events: List[WaylandEvent]
  requests: List[WaylandRequest]
```

```
class WaylandEnumEntry:
  name: string
  value: string
  summary: string | None

class WaylandEnum:
  name: string
  description: string | None
  entries: List[WaylandEnumEntry]
```

```
class WaylandEvent:
  name: string
  description: string | None
  args: List[WaylandArg]
```

```
class WaylandRequest:
  name: string
  description: string | None
  args: List[WaylandArg]
```
```
class WaylandArg:
  name: string
  type: wayland_type
  summary: string | None

type wayland_type = "uint" | "int" | "fixed" | "string" | "object" | "array" | "fd"
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

