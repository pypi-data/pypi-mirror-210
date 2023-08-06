import re
from .constants import VALUE_REGEX

intent = 0



def to_xml(obj):
    if type(obj) == tuple:
        serialized = []
        for el in obj:
            global intent
            intent += 1
            isType = False
            if type(el) == tuple:
                isType = True
                serialized.append(
                    f"\n"
                    + ((intent - 1) * "\t")
                    + f"<{type(el).__name__}>"
                    + (isType * intent * "\t")
                    + f"{to_xml(el)}"
                    + (isType * '\n')
                    + (isType * (intent - 1) * "\t")
                    + f"</{type(el).__name__}> "
                )
            else:
                serialized.append(
                    f"\n"
                    + ((intent - 1) * "\t")
                    + f"<str>"
                    + (isType * intent * "\t")
                    + f"{to_xml(el)}"
                    + (isType * '\n')
                    + (isType * (intent - 1) * "\t")
                    + f"</str> "
                )
            intent -= 1
        res = "".join(serialized)
        return f"{res}"
    else:
        return f"{str(obj)}"

string_count = 0
depth = 0

def from_xml(data: str):
    if data == '<tuple></tuple>':
        return tuple()
    elif data[:7] == '<tuple>':
        data = data[7:-9]
        if data[-1] == ' ':
            data = data[:-1]

        parsed = []
        depth = 0
        substr = ""
        for i in data:
            if i == '<' or i == '>':
                depth += 1
            elif i == '/':
                depth -= 4
            elif depth == 0:
                parsed.append(from_xml(substr))
                substr = ""
                continue

            substr += i
        parsed.append(from_xml(substr))
        return tuple(parsed)
    
    elif data[:5] == '<str>':
        parsed = []
        ind = data.find('</str>')
        if data[ind + 6:] != "":
            parsed.append(from_xml(data[5:ind]))
            parsed.append(from_xml(data[ind + 6:]))
        else:
            return data[5:ind]
        return tuple(parsed)
    else:
        return data