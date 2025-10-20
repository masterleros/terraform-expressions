import re
from expressions import ExpressionUnique, TokenType, ExpContext
from data import render, j_data


def get_type(variable: str):
    result = next(
        iter(re.findall(r"^i_(obj|list)_([a-zA-Z0-9_]{2,})$", variable)), None
    )
    if result:
        i_type = TokenType.INTERFACE if result[0] == "obj" else TokenType.INTERFACES
        return i_type, result[1]
    return None, None


def validate(context: ExpContext):
    s = [TokenType.PARENT, TokenType.PROVIDER, TokenType.MODULE_NAME]
    fs = context.get_found(s)
    fi = context.get_found([TokenType.INTERFACE, TokenType.INTERFACES])

    if not fs:
        raise ValueError(
            f"not a valid source for interface(s) (valid: {' | '.join[[s_name.value for s_name in s]]})"
        )

    match fs.id:
        case TokenType.PARENT | TokenType.PROVIDER:
            index = fs.id.value
            if fs.arguments[index] not in render[f"{index}s"]:
                raise ValueError(f"{index} '{fs.arguments[index]}' not found")
            if fi.arguments["type"] not in render[f"{index}s"][fs.arguments[index]].get(
                "outputs", {}
            ).get("interfaces", {}):
                raise ValueError(
                    f"Interface type '{fi.arguments["type"]}' not found in {index} '{fs.arguments[index]}'"
                )
        case TokenType.MODULE_NAME:
            if fs.value not in render["module"]:
                raise ValueError(f"module '{fs.value}' not found")

            if fi.render() not in render["module"][fs.value].get("outputs", {}):
                raise ValueError(
                    f"Interface type '{fi.render()}' not found in module '{fs.value}'"
                )


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
            raise ValueError(f"'{exp}' is not a valid interface expression")

        try:

            # Check interface
            i_found = e.context.get_found([TokenType.INTERFACE, TokenType.INTERFACES])
            if not i_found:
                raise ValueError(f"'{e.context.value}' is not an interface(s)")
            if i_found.arguments["type"] != var_i_type:
                raise ValueError(
                    f"Invalid interface type '{i_found.arguments["type"]}' (expected: '{var_i_type}')"
                )

            # Validate interface
            validate(e.context)

            # If unique interface object
            if var_i_id == TokenType.INTERFACE and i_found.id != TokenType.INTERFACE:
                raise ValueError(
                    f"Variable '{variable}' is an ojbect and does not support list of interfaces (use: interface() instead)"
                )
            # If list of interfaces assigning an object
            elif var_i_id == TokenType.INTERFACES and i_found.id == TokenType.INTERFACE:
                i_rendered.append(f"[{e.context.render()}]")
            # Else add it as it is
            else:
                i_rendered.append(e.context.render())

        except Exception as ex:
            raise type(ex)(f"Expression '{e.context.value}' error: {ex}")

    # Return based on ammount of interfaces assigned
    result = (
        i_rendered[0] if len(i_rendered) == 1 else f"flatten([{','.join(i_rendered)}])"
    )
    return f"${{{result}}}"
