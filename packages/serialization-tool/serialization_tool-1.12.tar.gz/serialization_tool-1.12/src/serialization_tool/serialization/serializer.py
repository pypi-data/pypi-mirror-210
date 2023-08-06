import inspect 
import re
from .constants import *
from types import CodeType, FunctionType
from pydoc import locate


class Serializer:

    def create_serializer(self, obj):
        if isinstance(obj, (float, int, complex, bool, str, type(None))):
            return self.serialize_type
        if isinstance(obj, (list, tuple, bytes, set)):
            return self.serialize_iterable
        if isinstance(obj, dict):
            return self.serialize_dict
        if inspect.isfunction(obj):
            return self.serialize_function
        if inspect.isclass(obj):
            return self.serialize_class
        if inspect.iscode(obj):
            return self.serialize_code
        if inspect.ismodule(obj):
            return self.serialize_module
        if inspect.ismethoddescriptor(obj) or inspect.isbuiltin(obj):
            return self.serialize_instance
        if inspect.isgetsetdescriptor(obj) or inspect.ismemberdescriptor(obj):
            return self.serialize_instance
        if isinstance(obj, type(type.__dict__)):
            return self.serialize_instance

        return self.serialize_object
    
    def serialize(self, obj):

        serializer = self.create_serializer(obj)
        serialized = serializer(obj)
        serialized = tuple((k, serialized[k]) for k in serialized)

        return serialized

    # fn to serialize primitive types
    def serialize_type(self, obj):
        
        result = dict()
        
        result[TYPE] = re.search(REGEX_TYPE, str(type(obj))).group(1)
        result[VALUE] = obj

        return result

    def serialize_iterable(self, obj):
        result = dict()

        result[TYPE] = re.search(REGEX_TYPE, str(type(obj))).group(1)
        result[VALUE] = tuple(self.serialize(val) for val in obj)

        return result
    
    def serialize_dict(self, obj: dict):
        result = dict()
        result[TYPE] = DICTIONARY
        result[VALUE] = {}

        for key, value in obj.items():
            key_result = self.serialize(key)
            value_result = self.serialize(value)
            result[VALUE][key_result] = value_result
        
        result[VALUE] = tuple((k, result[VALUE][k])
                            for k in result[VALUE])
        
        return result
    

    def serialize_function(self, function_object):
        result = dict()
        result[TYPE] = FUNCTION
        result[VALUE] = {}

        members = inspect.getmembers(function_object)
        members = [i for i in members if i[0] in FUNCTION_ATTRIBUTES]
        
        for i in members:
            key = self.serialize(i[0])
        
            if i[0] != CLOSURE:
                value = self.serialize(i[1])
            else:
                value = self.serialize(None)

            result[VALUE][key] = value
            if i[0] == CODE:
                key = self.serialize(GLOBALS)
                result[VALUE][key] = {}
                names = i[1].__getattribute__("co_names")
                
                glob = function_object.__getattribute__(GLOBALS)
                glob_dict = {}
                
                for name in names:
                    if name == function_object.__name__:
                        glob_dict[name] = function_object.__name__
                    elif name in glob and not inspect.ismodule(name) and name not in __builtins__:
                        glob_dict[name] = glob[name]
                
                result[VALUE][key] = self.serialize(glob_dict)

        result[VALUE] = tuple((k, result[VALUE][k]) for k in result[VALUE])
        return result
    
    
    def serialize_class(self, obj):
        ans = dict()
        ans[TYPE] = CLASS
        ans[VALUE] = {}
        ans[VALUE][self.serialize(NAME)] = self.serialize(obj.__name__)
        members = []
        for i in inspect.getmembers(obj):
            if not (i[0] in NOT_CLASS_ATTRIBUTES):
                members.append(i)

        for i in members:
            key = self.serialize(i[0])
            val = self.serialize(i[1])
            ans[VALUE][key] = val
        ans[VALUE] = tuple((k, ans[VALUE][k]) for k in ans[VALUE])

        return ans

    
    def serialize_object(self, some_object):
        class_obj = type(some_object)
        result = dict()
        result[TYPE] = OBJECT
        result[VALUE] = {}
        result[VALUE][self.serialize(OBJECT_NAME)] = self.serialize(class_obj)
        result[VALUE][self.serialize(FIELDS_NAME)] = self.serialize(some_object.__dict__)
        result[VALUE] = tuple((k, result[VALUE][k]) for k in result[VALUE])

        return result

    
    def serialize_instance(self, obj):
        result = dict()
        result[TYPE] = re.search(REGEX_TYPE, str(type(obj))).group(1)

        result[VALUE] = {}
        members = inspect.getmembers(obj)
        members = [i for i in members if not callable(i[1])]
        for i in members:
            key = self.serialize(i[0])
            val = self.serialize(i[1])
            result[VALUE][key] = val
        result[VALUE] = tuple((k, result[VALUE][k]) for k in result[VALUE])

        return result


    def serialize_code(self, obj):
        if re.search(REGEX_TYPE, str(type(obj))) is None:
            return None

        ans = dict()
        ans[TYPE] = re.search(REGEX_TYPE, str(type(obj))).group(1)

        ans[VALUE] = {}
        members = inspect.getmembers(obj)
        members = [i for i in members if not callable(i[1])]
        for i in members:
            key = self.serialize(i[0])
            val = self.serialize(i[1])
            ans[VALUE][key] = val
        ans[VALUE] = tuple((k, ans[VALUE][k]) for k in ans[VALUE])

        return ans

    def serialize_module(self, module):
        ans = dict()
        ans[TYPE] = MODULE_NAME
        ans[VALUE] = re.search(REGEX_TYPE, str(module)).group(1)

        return ans

    def create_deserializer(self, object_type):
        if object_type == DICTIONARY:
            return self.deserialize_dict
        if object_type == FUNCTION:
            return self.deserialize_function
        if object_type in ITERABLE_TYPES:
            return self.deserialize_iterable
        if object_type == CLASS:
            return self.deserialize_class
        if object_type in TYPES:
            return self.deserialize_type
        if object_type == OBJECT:
            return self.deserialize_object
        if object_type == MODULE_NAME:
            return self.deserialize_module
        
    def deserialize(self, obj):
        obj = dict((a, b) for a, b in obj)
        object_type = obj[TYPE]
        deserializer = self.create_deserializer(object_type)

        if deserializer is None:
            return

        return deserializer(object_type, obj[VALUE])


    def deserialize_type(self, object_type, obj):
        if object_type == TYPES[5]:
            return None

        if object_type == TYPES[2] and isinstance(obj, str):
            return obj == "True"

        return locate(object_type)(obj)    


    def deserialize_iterable(self, object_type, obj):
        result = []

        for value in obj:
            result.append(self.deserialize(value))

        if object_type == ITERABLE_TYPES[0]:
            return result
        elif object_type == ITERABLE_TYPES[1]:
            result = tuple(result)
        elif object_type == ITERABLE_TYPES[2]:
            result = set(result)
        else:
            result = bytes(result)

        return result
   
    def deserialize_dict(self, object_type, obj: dict):
        result = {}
        for i in obj:
            val = self.deserialize(i[1])
            result[self.deserialize(i[0])] = val

        return result
    

    def deserialize_function(self, object_type, foo):
        func = [0] * 4
        code = [0] * 16
        glob = {BUILTINS: __builtins__}

        for i in foo:
            key = self.deserialize(i[0])

            if key == GLOBALS:
                glob_dict = self.deserialize(i[1])
                for glob_key in glob_dict:
                    glob[glob_key] = glob_dict[glob_key]

            elif key == CODE:
                val = i[1][1][1]

                for arg in val:
                    code_arg_key = self.deserialize(arg[0])
                    if code_arg_key != DOC and code_arg_key != 'co_linetable':
                        code_arg_val = self.deserialize(arg[1])
                        index = CODE_OBJECT_ARGS.index(code_arg_key)
                        code[index] = code_arg_val

                code = CodeType(*code)
            else:
                index = FUNCTION_ATTRIBUTES.index(key)
                func[index] = (self.deserialize(i[1]))

        func[0] = code
        func.insert(1, glob)

        ans = FunctionType(*func)
        if ans.__name__ in ans.__getattribute__(GLOBALS):
            ans.__getattribute__(GLOBALS)[ans.__name__] = ans

        return ans
    
    def deserialize_object(self, object_type, obj):
        obj_dict = self.deserialize_dict(DICTIONARY, obj)
        result = obj_dict[OBJECT_NAME]()

        for key, value in obj_dict[FIELDS_NAME].items():
            result.key = value

        return result


    def deserialize_class(self, object_type, class_dict):
        some_dict = self.deserialize_dict(DICTIONARY, class_dict)
        name = some_dict[NAME]
        del some_dict[NAME]

        return type(name, (object,), some_dict)


    def deserialize_module(self, object_type, module_name):
        return __import__(module_name)


