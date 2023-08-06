from ..serialization import Serialization
from .utilities import to_json, from_json


class JsonSerialization(Serialization):
    def dump(self, obj, file):
        with open(file, "w") as f:
            f.write(self.dumps(obj))

    def dumps(self, obj):
        return to_json(self.serializer.serialize(obj)).replace("\n", "\\n")

    def load(self, file):
        with open(file, "r") as f:
            return self.loads(f.read())

    def loads(self, str):
        obj = from_json(str.replace("\\n", "\n"))
        return self.serializer.deserialize(obj)
