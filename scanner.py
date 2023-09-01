import sys
import xml.etree.ElementTree as ET


class ScannerError(Exception):
    pass


class UnknownTypeError(Exception):
    def __init__(self, t):
        super().__init__(f"Unknown type: {t}")


def validate_type(t):
    if (
        t == "uint"
        or t == "int"
        or t == "fixed"
        or t == "string"
        or t == "object"
        or t == "new_id"
        or t == "array"
        or t == "fd"
    ):
        return t
    else:
        raise UnknownTypeError(t)


def option_map(value, f):
    if value != None:
        return f(value)
    else:
        return value


class Name:
    def __init__(self, name):
        assert name
        self.name = name

    def snake(self):
        return self.name

    def screaming(self):
        return self.name.upper()

    def pascal(self):
        return "".join([word.capitalize() for word in self.name.split("_")])

    def camel(self):
        return self._uncapitalise(self.pascal())

    def text(self):
        return self.name.replace("_", " ")

    def _uncapitalize(self, string):
        return s[:1].lower() + s[1:]

    def __add__(self, other_name):
        if type(other_name) == str:
            return Name(self.name + "_" + other_name.lower())
        elif type(other_name) == Name:
            return Name(self.name + "_" + other_name.name)
        else:
            raise TypeError(f"Can't add Name to {type(other_name)}")


class Description:
    def __init__(self, root):
        self.text = (
            "\n".join([line.strip() for line in root.text.splitlines()])
            if root.text
            else ""
        )
        self.summary = option_map(root.attrib.get("summary"), lambda s: s.strip())

    def __repr__(self):
        return self.summary


class EnumEntry:
    def __init__(self, root):
        self.name = Name(root.attrib["name"])
        self.value = root.attrib["value"]
        self.summary = root.attrib.get("summary")

    def __repr__(self):
        return f"\t\t\t{self.name} ({self.value})"


class Enum:
    def __init__(self, root):
        self.name = Name(root.attrib["name"])
        self.description = None
        self.entries = []

        for child in root:
            if child.tag == "description":
                self.description = Description(child)
            elif child.tag == "entry":
                self.entries.append(EnumEntry(child))
            else:
                raise ScannerError(f'Unknown item in enum: "{child.tag}"')

    def __repr__(self):
        return f"\t\tEnum '{self.name}':\n" + "\n".join(
            map(lambda e: e.__repr__(), self.entries)
        )


class Arg:
    def __init__(self, root):
        self.name = Name(root.attrib["name"])
        self.type = validate_type(root.attrib["type"])
        self.interface = option_map(root.attrib.get("interface"), Name)
        self.nullable = root.attrib.get("allow-null") == "true"
        self.summary = root.attrib.get("summary")

    def is_interface(self):
        return self.type == "new_id"

    def __repr__(self):
        return f"{self.name}: {self.type}"


class ArgList:
    def __init__(self):
        self.args = []

    def add_arg(self, arg):
        self.args.append(arg)

    def return_arg(self):
        for arg in self.args:
            if arg.is_interface():
                return arg

    def parameters(self):
        for arg in self.args:
            if arg.is_interface() and arg.interface != None:
                continue
            yield arg

    def marshal_arguments(self):
        for arg in self.args:
            yield arg

    def __repr__(self):
        return "(" + ",".join(map(lambda a: a.__repr__(), self.args)) + ")"


class Event:
    def __init__(self, root):
        self.name = Name(root.attrib["name"])
        self.description = None
        self.args = []

        for child in root:
            if child.tag == "description":
                self.description = Description(child)
            elif child.tag == "arg":
                self.args.append(Arg(child))
            else:
                raise ScannerError(f'Unknown item in event: "{child.tag}"')

    def __repr__(self):
        return f"\t\tEvent '{self.name}' " + self.args.__repr__()


class Request:
    def __init__(self, root):
        self.name = Name(root.attrib["name"])
        self.description = None
        self.is_destructor = root.attrib.get("type") == "destructor"
        self.args = ArgList()

        for child in root:
            if child.tag == "description":
                self.description = Description(child)
            elif child.tag == "arg":
                self.args.add_arg(Arg(child))
            else:
                raise ScannerError(f'Unknown item in request: "{child.tag}"')

    def __repr__(self):
        return f"\t\tRequest '{self.name}' " + self.args.__repr__()


class Interface:
    def __init__(self, root):
        self.name = Name(root.attrib["name"])
        self.description = None

        self.enums = []
        self.events = []
        self.requests = []

        for child in root:
            if child.tag == "description":
                self.description = Description(child)
            elif child.tag == "enum":
                self.enums.append(Enum(child))
            elif child.tag == "event":
                self.events.append(Event(child))
            elif child.tag == "request":
                self.requests.append(Request(child))
            else:
                raise ScannerError(f'Unknown item in interface: "{child.tag}"')

    def __repr__(self):
        return (
            f"\tInterface '{self.name}':\n"
            + "\n".join(map(lambda e: e.__repr__(), self.enums))
            + "\n"
            + "\n".join(map(lambda e: e.__repr__(), self.events))
            + "\n"
            + "\n".join(map(lambda r: r.__repr__(), self.requests))
        )


class Specification:
    def __init__(self, root):
        assert root.tag == "protocol"
        self.name = Name(root.attrib["name"])
        self.copyright = None
        self.interfaces = []

        for child in root:
            if child.tag == "copyright":
                self.copyright = child.text
            elif child.tag == "interface":
                self.interfaces.append(Interface(child))
            else:
                raise ScannerError(f'Unknown item in specification: "{child.tag}"')

    def __repr__(self):
        return f"Protocol '{self.name}':\n" + "\n\n".join(
            map(lambda ch: ch.__repr__(), self.interfaces)
        )


def print_help():
    print("Usage: python scanner.py < [protocol-description.xml]")


def parse_string(string):
    root = ET.fromstring(string)
    return Specification(root)


def parse_stdin():
    return parse_string(sys.stdin.read())


def run():
    if len(sys.argv) > 1:
        print_help()
    else:
        print(parse_stdin())


if __name__ == "__main__":
    run()
