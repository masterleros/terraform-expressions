import re
from expressions import ExpressionUnique, TokenType


def get_type(variable: str):
    result = next(
        iter(re.findall(r"^i_(obj|list)_([a-zA-Z0-9_]{2,})$", variable)), None
    )
    if result:
        i_type = TokenType.INTERFACE if result[0] == "obj" else TokenType.INTERFACES
        return i_type, result[1]
    return None, None


def assign(variable: str, expression: str | list) -> str:

    # Check variable
    var_i_id, var_i_type = get_type(variable)
    if not var_i_id:
        raise ValueError(
            f"Variable '{variable}' is not an interface (expected: i_obj_<type> | i_list_<type>)"
        )

    # Validate type
    if (
        var_i_id == TokenType.INTERFACE
        and type(expression) != str
        or var_i_id == TokenType.INTERFACES
        and type(expression) not in [str, list]
    ):
        raise ValueError(
            f"Variable '{variable}' does not support '{type(expression).__name__}' assigments"
        )
    # If string make it a single item list
    elif type(expression) == str:
        expression = [expression]

    # For each interface expression
    i_rendered = []
    for exp in expression:
        e = ExpressionUnique(exp)
        if not e.extracted:
            raise ValueError(
                f"Expression '{exp}' is not a valid single interface(s) expression"
            )

        # Check interface
        i_id = next(
            iter(
                set(e.context.types) & set([TokenType.INTERFACE, TokenType.INTERFACES])
            ),
            None,
        )
        i_type = e.context.get_id(i_id).arguments["type"] if i_id else None
        if not i_id:
            raise ValueError(f"'{e.context.value}' is not an interface(s)")
        if i_type != var_i_type:
            raise ValueError(
                f"Invalid interface type '{i_type}' in '{e.context.value}' (expected: '{var_i_type}')"
            )

        # If unique interface object
        if var_i_id == TokenType.INTERFACE and i_id != TokenType.INTERFACE:
            raise ValueError(
                f"Variable '{variable}' is an ojbect and does not support list of interfaces (use: interface() instead)"
            )
        # If list of interfaces assigning an object
        elif var_i_id == TokenType.INTERFACES and i_id == TokenType.INTERFACE:
            i_rendered.append(f"[{e.context.render()}]")
        # Else add it as it is
        else:
            i_rendered.append(e.context.render())

    # Return based on ammount of interfaces assigned
    result = (
        i_rendered[0] if len(i_rendered) == 1 else f"flatten([{','.join(i_rendered)}])"
    )
    return f"${{{result}}}"
