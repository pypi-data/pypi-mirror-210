from abc import ABC, abstractmethod
from serialization_tool.serialization.serializer import Serializer

class Serialization(ABC):
    def __init__(self):
        self.serializer = Serializer()
    
    @abstractmethod
    def dump(self, obj, file):
        """ Serialize your object to file.
        Pass as second parameter file and after running your object will be serialized to this file.
        """
        pass

    @abstractmethod
    def dumps(self, obj):
        """Serialize your object to string. 
        Returning serialized object as string
        """
        pass

    @abstractmethod
    def load(self, file):
        """ Deserialize your object from file.
        Pass as second parameter file and after running your object will be deserialized from this file.
        """
        pass

    @abstractmethod
    def loads(self, str):
        """Deserialize your object from string. 
        Returning deserialized object as object
        """
        pass
    