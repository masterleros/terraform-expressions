import json
from expressions import Expression, TokenType
import re


render = {
    "tfcode": {
        "variable": {},
        "local": {},
        "module": {
            "test1": {"outputs": {"i_kms": {"data": "value1"}}},
            "test2": {"outputs": {"i_kms": {"data": "value2"}}},
            "test3": {"outputs": {"i_kms": {"data": "value3"}}},
        },
        "data": {},
        "resource": {},
        "output": {},
    },
    "parents": {"test": {"id": "123-test"}, "base": {"id": "123-base"}},
    "providers": {"base": {"id": "000-base"}},
}

expressions = [
    "${parent(base).interfaces(kms,mykms)}",
    "${provider(base).interfaces(kms,mykms)}",
    "${module.test.an_output}",
    "${module.test.interfaces(kms)}",
    "${var.test}",
]

# try:
#     for expression in expressions:
#         e = Expression(expression)
#         print(e.render())

#         # Validation
#         for c in e.contextes:
#             for f in c.found:
#                 match f.id:
#                     case TokenType.PARENT:
#                         if f.arguments["parent"] not in render["parents"]:
#                             raise ValueError(
#                                 f"parent '{f.arguments['parent']}' not found"
#                             )
#                     case TokenType.PROVIDER:
#                         if f.arguments["provider"] not in render["providers"]:
#                             raise ValueError(
#                                 f"provider '{f.arguments['provider']}' not found"
#                             )
#                     case TokenType.MODULE_NAME:
#                         if f.value not in render["tfcode"]["module"]:
#                             raise ValueError(f"module '{f.value}' not found")

#                     case TokenType.VARIABLE_NAME:
#                         if f.value not in render["tfcode"]["variable"]:
#                             render["tfcode"]["variable"][f.value] = {}
#                     case TokenType.LOCAL_NAME:
#                         if f.value not in render["tfcode"]["local"]:
#                             render["tfcode"]["local"][f.value] = {}

# except Exception as e:
#     raise type(e)(f"Validation Error: {e}")

# Show render result
# print(json.dumps(render, indent=2))


def get_i_type(interface: str):
    return next(iter(re.findall(r"i_([a-zA-Z0-9_]{2,})$", interface)), None)
    # if not i:
    #     raise ValueError(f"Invalid interface '{interface}' (expected: 'i_<type>')")
    # return i


def validate_interface(assignment: str, expression: str):
    exp = Expression(expression)
    i_type = get_i_type(assignment)
    for c in exp.contextes:
        i = next(iter([f for f in c.found if f.id == TokenType.INTERFACES]), None)
        if not i:
            raise ValueError(f"No interfaces found in '{c.value}'")
        if i.arguments["type"] != i_type:
            raise ValueError(
                f"Invalid interface type '{i.arguments['type']}' in '{c.value}' (expected: '{i_type}')"
            )


# print(validate_interface("i_kms", "${module.test.interfaces(kms)}"))


interfaces = {}
id = "123-abc"
for m_name, m_data in render["tfcode"]["module"].items():
    for o_name, o_data in m_data.get("outputs", {}).items():
        i = get_i_type(o_name)
        if i:
            if not i in interfaces:
                interfaces[i] = {}
            interfaces[i][f"{id}.{m_name}"] = o_data


print(json.dumps(interfaces, indent=2))
