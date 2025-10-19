from enum import Enum
from expression_processor import (
    ExpProcessor,
    ExpContext,
    ExpFound,
    ExpProcessorCollection,
)


class TokenType(Enum):
    COLLECTOR = "collector"
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


class ExpProcessorInterface(ExpProcessor):
    def __init__(self):
        super().__init__(
            TokenType.INTERFACE,
            f"interface",
            arguments={"type": str, "id": str},
            f_render=self.render,
        )

    def render(self, context: ExpContext, item: ExpFound):
        context.embrace = f"local.i_data.{item.arguments['type']}[\"{{result}}-{item.arguments['id']}\"]"


class ExpProcessorInterfaces(ExpProcessor):
    def __init__(self):
        super().__init__(
            TokenType.INTERFACES,
            f"interfaces",
            arguments={"type": str, "id": None},
            f_render=self.render,
        )

    def render(self, context: ExpContext, item: ExpFound):
        context.embrace = (
            (
                f"[ local.i_data.{item.arguments['type']}[\"{{result}}-{item.arguments['id']}\"] ]"
            )
            if "id" in item.arguments
            else (
                f"[ for ik, iv in local.i_data.{item.arguments['type']} : iv if startswith(ik, \"{{result}}\") ]"
            )
        )


def collector_render(context: ExpContext, item: ExpFound):
    match item.arguments.get("source", None):
        case "module":
            ...
        case "parent" | "provider":
            return f"[ for ik, iv in local.i_data.{item.arguments['type']} : iv if startswith(ik, \"{item.arguments['source']}-\") ]"
        case None:
            return f"[ for iv in local.i_data.{item.arguments['type']}: iv ]"
        case _:
            raise ValueError(
                f"collector source '{item.arguments['source']}' is not valid (expected: module | parent | provider)"
            )


class ExpProcessorOutputs(ExpProcessor):
    def __init__(self):
        super().__init__(
            TokenType.OUTPUTS,
            "outputs",
            last_match=True,
        )


class Expression(list):

    # Configure processor
    tf_processor = ExpProcessorCollection(
        [
            ExpProcessor(
                TokenType.COLLECTOR,
                f"collector",
                arguments={"type": str, "source": None},
                f_render=collector_render,
            ),
            ExpProcessor(
                TokenType.PARENT,
                f"parent",
                arguments={"parent": str},
                children=[
                    ExpProcessorInterface(),
                    ExpProcessorInterfaces(),
                    ExpProcessorOutputs(),
                ],
                f_render=lambda c, i: f"parent-{i.arguments['parent']}",
            ),
            ExpProcessor(
                TokenType.PROVIDER,
                f"provider",
                arguments={"provider": str},
                children=[
                    ExpProcessorInterface(),
                    ExpProcessorInterfaces(),
                    ExpProcessorOutputs(),
                ],
                f_render=lambda c, i: f"provider-{i.arguments['provider']}",
            ),
            ExpProcessor(
                TokenType.MODULE,
                r"module",
                children=[
                    ExpProcessor(
                        TokenType.MODULE_NAME,
                        children=[
                            ExpProcessor(
                                TokenType.INTERFACE,
                                f"interface",
                                arguments={"type": str},
                                f_render=lambda c, i: f"i_{i.arguments['type']}",
                            ),
                            ExpProcessor(
                                TokenType.INTERFACES,
                                f"interfaces",
                                unsupported=True,
                            ),
                            ExpProcessor(
                                TokenType.MODULE_OUTPUT,
                                last_match=True,
                            ),
                        ],
                    ),
                ],
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
        expression = None
        for context in self.contextes:
            expression = self.tf_processor.replace(
                self.expression, context.value, context.render()
            )
        return expression
