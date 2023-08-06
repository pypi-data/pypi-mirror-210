import pathlib
import typing
import xml.etree.cElementTree

from ..__type import FileProvider


class XMLProvider(FileProvider):
    def search_write(self, root, data: typing.Dict[str, typing.Any]) -> None:
        root: xml.etree.cElementTree.Element = root
        for k, v in data.items():
            e = xml.etree.cElementTree.Element(k)
            root.append(e)
            if not isinstance(v, dict):
                e.text = f'"{v}"' if isinstance(v, str) else str(v)
            else:
                self.search_write(e, v)

    def search_read(self, root, data: dict) -> None:
        root: xml.etree.cElementTree.Element = root
        for e in root.findall("*"):
            childs = e.findall("*")
            if len(childs) == 0:
                data[e.tag] = e.text
            else:
                data[e.tag] = {}
                self.search_read(e, data[e.tag])

    def read(self, path: pathlib.Path) -> dict:
        with open(path, 'r', encoding='utf-8') as file:
            tree = xml.etree.cElementTree.parse(file)
        data = {}
        self.search_read(tree.getroot(), data)
        return data

    def write(self, path: pathlib.Path, data: dict) -> None:
        root = xml.etree.cElementTree.Element('root')
        self.search_write(root, data)
        xml.etree.cElementTree.ElementTree(root).write(self.path)
