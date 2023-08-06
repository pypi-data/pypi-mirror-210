from ..serialization import Serialization
from .constants import TYPES
from .utilities import to_xml, from_xml


class XmlSerialization(Serialization):
    def dump(self, obj, file):
        with open(file, "w") as f:
            f.write(self.dumps(obj))

    def dumps(self, obj):
        res = to_xml(self.serializer.serialize(obj)).replace('\n', '\n\t')
        res = "\n<tuple>" + res + "\n</tuple>"
        return res.replace(
            "\n", '<?xml version="1.0" encoding="utf-8"?>\n', 1
        )

    def load(self, file):
        with open(file, "r") as f:
            return self.loads(f.read())

    def loads(self, data: str):
        data = data.replace('<?xml version="1.0" encoding="utf-8"?>\n', '')
        data = data.replace('\n', '').replace('\t', '')
        return self.serializer.deserialize(from_xml(data))
