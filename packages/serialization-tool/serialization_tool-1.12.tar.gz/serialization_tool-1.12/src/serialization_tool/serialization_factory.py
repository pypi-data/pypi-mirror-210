from serialization_tool.types.json.json import JsonSerialization
from serialization_tool.types.xml.xml import XmlSerialization

# import constants as const
from .constants import *

class SerializationFactory:

    def get_serializer(ext: str):
        """ Method for getting serializer to type, which you want.
        Pass to method string with type name, which you want to serialize,
        for example "json".
        Method return serializer with methods dump, load, dumps, loads
        """
        if ext == JSON_EXT:
            return JsonSerialization()
        elif ext == XML_EXT:
            return XmlSerialization()
        else:
            print("Unknown type to parse")
                