from data import expressions, render
from expressions import Expression, TokenType
import json

try:
    for expression in expressions:
        e = Expression(expression)
        print(e.render())

        # Validation
        for c in e.contextes:
            for f in c.found:
                match f.id:
                    case TokenType.PARENT:
                        if f.arguments["parent"] not in render["parents"]:
                            raise ValueError(
                                f"parent '{f.arguments['parent']}' not found"
                            )
                    case TokenType.PROVIDER:
                        if f.arguments["provider"] not in render["providers"]:
                            raise ValueError(
                                f"provider '{f.arguments['provider']}' not found"
                            )
                    case TokenType.MODULE_NAME:
                        if f.value not in render["tfcode"]["module"]:
                            raise ValueError(f"module '{f.value}' not found")

                    case TokenType.VARIABLE_NAME:
                        if f.value not in render["tfcode"]["variable"]:
                            render["tfcode"]["variable"][f.value] = {}
                    case TokenType.LOCAL_NAME:
                        if f.value not in render["tfcode"]["local"]:
                            render["tfcode"]["local"][f.value] = {}

except Exception as e:
    raise type(e)(f"Validation Error: {e}")

# Show render result
print(json.dumps(render, indent=2))
