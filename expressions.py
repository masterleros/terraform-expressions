from enum import Enum
from expression_processor import (
    ExpProcessor,
    ExpContext,
    ExpFound,
    ExpProcessorCollection,
)


class TokenType(Enum):
    INTERFACES = "interfaces"
    INTERFACE = "interface"
    OUTPUTS = "outputs"
    PARENT = "parent"
    PROVIDER = "provider"
    VARIABLE = "variable"
    VARIABLE_NAME = "variable name"
    LOCAL = "local"
    LOCAL_NAME = "local name"
    MODULE = "module"
    MODULE_NAME = "module name"
    MODULE_OUTPUT = "module output"
    DATA = "data"
    DATA_TYPE = "data type"
    DATA_NAME = "data name"
    RESOURCE = "resource"
    RESOURCE_TYPE = "resource type"
    RESOURCE_NAME = "resource name"


def interfaces_render(context: ExpContext, item: ExpFound):
    result = f"i_{item.arguments['type']}"
    if "id" in item.arguments:
        context.embrace = (
            f"[ for i in {{result}}: i.data if i.id == \"{item.arguments['id']}\"]"
        )
    return result


class ExpProcessorInterfaces(ExpProcessor):
    def __init__(self):
        super().__init__(
            TokenType.INTERFACES,
            f"interfaces",
            arguments={"type": str, "id": None},
            f_render=interfaces_render,
        )


class ExpProcessorOutputs(ExpProcessor):
    def __init__(self):
        super().__init__(
            TokenType.OUTPUTS,
            "outputs",
            last_match=True,
            # f_render=lambda c, i: ".".join(i.get("remaining", [])),
        )


class Expression(list):

    # Configure processor
    tf_processor = ExpProcessorCollection(
        [
            ExpProcessor(
                TokenType.PARENT,
                f"parent",
                arguments={"parent": str},
                children=[
                    ExpProcessorInterfaces(),
                    ExpProcessorOutputs(),
                ],
                f_render=lambda c, i: f"data.tfm[\"{i.arguments['parent']}\"].values",
            ),
            ExpProcessor(
                TokenType.PROVIDER,
                f"provider",
                arguments={"provider": str},
                children=[
                    ExpProcessorInterfaces(),
                    ExpProcessorOutputs(),
                ],
                f_render=lambda c, i: f"data.tfm[\"{i.arguments['provider']}\"].values",
            ),
            ExpProcessor(
                TokenType.VARIABLE,
                r"var",
                children=[
                    ExpProcessorInterfaces(),
                    ExpProcessor(
                        TokenType.VARIABLE_NAME,
                        last_match=True,
                    ),
                ],
            ),
            ExpProcessor(
                TokenType.LOCAL,
                r"local",
                children=[
                    ExpProcessorInterfaces(),
                    ExpProcessor(
                        TokenType.LOCAL_NAME,
                        last_match=True,
                    ),
                ],
            ),
            ExpProcessor(
                TokenType.MODULE,
                r"module",
                children=[
                    ExpProcessor(
                        TokenType.MODULE_NAME,
                        children=[
                            ExpProcessorInterfaces(),
                            ExpProcessor(
                                TokenType.MODULE_OUTPUT,
                                last_match=True,
                            ),
                        ],
                    ),
                ],
            ),
            ExpProcessor(
                TokenType.DATA,
                r"data",
                children=[
                    ExpProcessor(
                        TokenType.DATA_TYPE,
                        children=[ExpProcessor(TokenType.DATA_NAME, last_match=True)],
                    )
                ],
            ),
            ExpProcessor(
                TokenType.RESOURCE,
                r"resource",
                children=[
                    ExpProcessor(
                        TokenType.RESOURCE_TYPE,
                        children=[
                            ExpProcessor(TokenType.RESOURCE_NAME, last_match=True)
                        ],
                    )
                ],
            ),
        ]
    )

    def __init__(self, expression: str):
        self.expression = expression
        self.extracted = self.tf_processor.extract(expression)
        self.contextes = [self.tf_processor.parse(value) for value in self.extracted]

    def render(self):
        for context in self.contextes:
            expression = self.tf_processor.replace(
                self.expression, context.value, self.tf_processor.render(context)
            )
        return expression
