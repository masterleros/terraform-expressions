import json
from expressions import Expression, TokenType
from data import render, j_data
from interfaces import get_type
import tfcode


# def get_i_type(interface: str):
#     return next(iter(re.findall(r"i_([a-zA-Z0-9_]{2,})$", interface)), None)
#     # if not i:
#     #     raise ValueError(f"Invalid interface '{interface}' (expected: 'i_<type>')")
#     # return i


def assign_interface(variable: str, expression: str) -> str:

    # Check variable
    var_i_id, var_i_type = get_type(variable)
    if not var_i_id:
        raise ValueError(
            f"Variable '{variable}' is not an interface (expected: i_obj_<type> | i_list_<type>)"
        )

    # Check expresion
    exp = Expression(expression)
    if len(exp.contextes) < 1:
        raise ValueError(f"Expression '{expression}' does not contain any interface")

    i_rendered = []
    for c in exp.contextes:
        i = next(
            iter(
                [
                    f
                    for f in c.found
                    if f.id in [TokenType.INTERFACE, TokenType.INTERFACES]
                ]
            ),
            None,
        )

        # Check interface
        if not i:
            raise ValueError(f"'{c.value}' is not an interface(s)")
        elif i.arguments["type"] != var_i_type:
            raise ValueError(
                f"Invalid interface type '{i.arguments['type']}' in '{c.value}' (expected: '{var_i_type}')"
            )

        # If unique interface object
        if var_i_id == TokenType.INTERFACE:
            # If assigning an object and is unique
            if not i_rendered and i.id == TokenType.INTERFACE:
                i_rendered.append(c.render())
            else:
                raise ValueError(
                    f"Variable '{variable}' is an ojbect and does not support multiple interfaces assigment (use: interface())"
                )

        # If list of interfaces
        elif var_i_id == TokenType.INTERFACES:
            if i.id == TokenType.INTERFACE:
                i_rendered.append(f"[{c.render()}]")
            else:
                i_rendered.append(c.render())

    # Return based on ammount of interfaces assigned
    result = (
        i_rendered[0]
        if len(exp.contextes) == 1
        else f"flatten([{','.join(i_rendered)}])"
    )
    return f"${{{result}}}"


var = "i_list_kms"
exp = "${parent(base).interfaces(kms),parent(test).interfaces(kms,test1)}"
# print("var = " + str(assign_interface(var, exp)))

j_data = {
    "locals": [
        {
            "__block__": True,
            "i_data": "${{ for i_type in distinct(flatten([for value in values(local.parents) : keys(value.interfaces)])) : i_type => { for i in flatten([for p_name, p_values in local.parents : ["
            'for i_id, i_values in lookup(p_values.interfaces, i_type, {}) : { id = "${p_name}-${i_id}", values = i_values }'
            "]]) : i.id => i.values } } }",
        }
    ],
    "output": [
        {
            "i_obj_kms": {
                "__block__": True,
                "value": str(
                    assign_interface(
                        "i_obj_kms", "${parent(base).interface(kms,test1)}"
                    )
                ),
            }
        },
        {
            "i_list_kms_filtered": {
                "__block__": True,
                "value": str(
                    assign_interface(
                        "i_list_kms",
                        "${parent(base).interfaces(kms,test1),parent(test).interfaces(kms,test1)}",
                    )
                ),
            }
        },
        {
            "i_list_kms": {
                "__block__": True,
                "value": str(
                    assign_interface(
                        "i_list_kms",
                        "${parent(base).interfaces(kms)}",
                    )
                ),
            }
        },
        # {"i_data": {"__block__": True, "value": "${local.i_data}"}},
    ],
}

# print(json.dumps(j_data, indent=2))

# Remove empty resources and write file
tfcode.write("test.tf", {i: j_data[i] for i in j_data if j_data[i] != []})
