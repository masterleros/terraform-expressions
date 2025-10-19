import re
from expressions import TokenType


def get_type(variable: str):
    result = next(
        iter(re.findall(r"^i_(obj|list)_([a-zA-Z0-9_]{2,})$", variable)), None
    )
    if result:
        i_type = TokenType.INTERFACE if result[0] == "obj" else TokenType.INTERFACES
        return i_type, result[1]
    return None, None
