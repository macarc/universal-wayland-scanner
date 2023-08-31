import sys
import xml.etree.ElementTree as ET

class ScannerError(Exception):
    pass

class UnknownTypeError(Exception):
    def __init__(self, t):
        super().__init__(f'Unknown type: {t}')

def validate_type(t):
    if t == 'uint' or t == 'int' or t == 'fixed' or t == 'string' or t == 'object' or t == 'new_id' or t == 'array' or t == 'fd':
        return t
    else:
        raise UnknownTypeError(t)

class WaylandEnumEntry:
    def __init__(self, root):
        self.name = root.attrib['name']
        self.value = root.attrib['value']
        self.summary = root.attrib.get('summary')

    def __repr__(self):
        return f'\t\t\t{self.name} ({self.value})'

class WaylandEnum:
    def __init__(self, root):
        self.name = root.attrib['name']
        self.entries = []

        for child in root:
            if child.tag == 'description':
                self.description = child.text
            elif child.tag == 'entry':
                self.entries.append(WaylandEnumEntry(child))
            else:
                raise ScannerError(f'Unknown item in enum: "{child.tag}"')

    def __repr__(self):
        return f'\t\tEnum \'{self.name}\':\n' + '\n'.join(map(lambda e: e.__repr__(), self.entries))

class WaylandArg:
    def __init__(self, root):
        self.name = root.attrib['name']
        self.type = validate_type(root.attrib['type'])
        self.summary = root.attrib['summary']

    def __repr__(self):
        return f'{self.name}: {self.type}'

class WaylandEvent:
    def __init__(self, root):
        self.name = root.attrib['name']
        self.args = []

        for child in root:
            if child.tag == 'description':
                self.description = child.text
            elif child.tag == 'arg':
                self.args.append(WaylandArg(child))
            else:
                raise ScannerError(f'Unknown item in event: "{child.tag}"')

    def __repr__(self):
        return f'\t\tEvent \'{self.name}\' (' + ', '.join(map(lambda a: a.__repr__(), self.args)) + ')'


class WaylandRequest:
    def __init__(self, root):
        self.name = root.attrib['name']
        self.args = []

        for child in root:
            if child.tag == 'description':
                self.description = child.text
            elif child.tag == 'arg':
                self.args.append(WaylandArg(child))
            else:
                raise ScannerError(f'Unknown item in request: "{child.tag}"')

    def __repr__(self):
        return f'\t\tRequest \'{self.name}\' (' + ', '.join(map(lambda a: a.__repr__(), self.args)) + ')'

class WaylandInterface:
    def __init__(self, root):
        self.name = root.attrib['name']

        self.enums = []
        self.events = []
        self.requests = []

        for child in root:
            if child.tag == 'description':
                self.description = child.text
            elif child.tag == 'enum':
                self.enums.append(WaylandEnum(child))
            elif child.tag == 'event':
                self.events.append(WaylandEvent(child))
            elif child.tag == 'request':
                self.requests.append(WaylandRequest(child))
            else:
                raise ScannerError(f'Unknown item in interface: "{child.tag}"')

    def __repr__(self):
        return f'\tInterface \'{self.name}\':\n' + '\n'.join(map(lambda e: e.__repr__(), self.enums)) + '\n' + '\n'.join(map(lambda e: e.__repr__(), self.events)) + '\n' + '\n'.join(map(lambda r: r.__repr__(), self.requests))


class WaylandSpecification:
    def __init__(self, root):
        assert(root.tag == 'protocol')
        self.name = root.attrib['name']
        self.interfaces = []

        for child in root:
            if child.tag == 'copyright':
                self.copyright = child.text
            elif child.tag == 'interface':
                self.interfaces.append(WaylandInterface(child))
            else:
                raise ScannerError(f'Unknown item in specification: "{child.tag}"')

    def __repr__(self):
        return f'Protocol \'{self.name}\':\n' + '\n\n'.join(map(lambda ch: ch.__repr__(), self.interfaces))


def print_help():
    print("Usage: python scanner.py < [protocol-description.xml]")

def parse_string(string):
    root = ET.fromstring(string)
    return WaylandSpecification(root)

def parse_stdin():
    return parse_string(sys.stdin.read())

def run():
    if len(sys.argv) > 1:
        print_help()
    else:
        print(parse_stdin())


if __name__ == "__main__":
    run()
