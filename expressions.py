from expression_processor import (
    ExpProcessor,
    ExpContext,
    ExpFound,
    ExpProcessorCollection,
)


class ExpProcessorInterfaces(ExpProcessor):
    def __init__(self):
        super().__init__(
            "Interfaces",
            f"interfaces",
            arguments={"type": str, "id": None},
            f_render=self._render,
        )

    def _render(self, context: ExpContext, item: ExpFound):
        result = f"i_{item.arguments['type']}"
        if "id" in item.arguments:
            context.embrace = (
                f"[ for i in {{result}}: i.data if i.id == \"{item.arguments['id']}\"]"
            )
        return result


class ExpProcessorTfeOutputs(ExpProcessor):
    def __init__(self):
        super().__init__(
            "TFE Outputs",
            "outputs",
            last_match=True,
            f_render=lambda c, i: ".".join(i.get("remaining", [])),
        )


def validate_parent(c: ExpContext, i: ExpFound, render: dict):
    if i.arguments["parent"] not in render["parents"]:
        raise Exception(f"Parent '{i.arguments['parent']}' does not exist")


def validate_provider(c: ExpContext, i: ExpFound, render: dict):
    if i.arguments["provider"] not in render["providers"]:
        raise Exception(f"Provider '{i.arguments['provider']}' does not exist")


def validate_module(c: ExpContext, i: ExpFound, render: dict):
    if i.value not in render["tfcode"]["module"]:
        raise Exception(f"Module '{i.value}' not found")


class Expression(list):

    # Configure processor
    tf_processor = ExpProcessorCollection(
        [
            ExpProcessor(
                "Parent Target",
                f"parent",
                arguments={"parent": str},
                children=[
                    ExpProcessorInterfaces(),
                    ExpProcessorTfeOutputs(),
                ],
                f_render=lambda c, i: f"data.tfm[\"{i.arguments['parent']}\"].values",
                f_process=validate_parent,
            ),
            ExpProcessor(
                "Provider Target",
                f"provider",
                arguments={"provider": str},
                children=[
                    ExpProcessorInterfaces(),
                    ExpProcessorTfeOutputs(),
                ],
                f_render=lambda c, i: f"data.tfm[\"{i.arguments['provider']}\"].values",
                f_process=validate_provider,
            ),
            ExpProcessor(
                "Variable",
                r"var",
                children=[
                    ExpProcessorInterfaces(),
                    ExpProcessor(
                        "Variable Name",
                        last_match=True,
                        f_process=lambda c, i, render: render["tfcode"][
                            "variable"
                        ].update({i.value: {}}),
                    ),
                ],
            ),
            ExpProcessor(
                "Local",
                r"local",
                children=[
                    ExpProcessorInterfaces(),
                    ExpProcessor(
                        "Local Name",
                        last_match=True,
                        f_process=lambda c, i, render: render["tfcode"]["local"].update(
                            {i.value: {}}
                        ),
                    ),
                ],
            ),
            ExpProcessor(
                "Module",
                r"module",
                children=[
                    ExpProcessorInterfaces(),
                    ExpProcessor(
                        "Module Name", last_match=True, f_process=validate_module
                    ),
                ],
            ),
            ExpProcessor(
                "Data",
                r"data",
                children=[
                    ExpProcessor(
                        "Data Type",
                        children=[ExpProcessor("Data Name", last_match=True)],
                    )
                ],
            ),
            ExpProcessor(
                "Resource",
                r"resource",
                children=[
                    ExpProcessor(
                        "Resource Type",
                        children=[ExpProcessor("Resource Name", last_match=True)],
                    )
                ],
            ),
        ]
    )

    def __init__(self, expression: str):
        self.expression = expression
        self.extracted = self.tf_processor.extract(expression)
        self.contextes = [self.tf_processor.parse(value) for value in self.extracted]

    def process(self, tfcode: dict):
        [self.tf_processor.process(context, tfcode) for context in self.contextes]

    def render(self):
        for context in self.contextes:
            expression = self.tf_processor.replace(
                self.expression, context.value, self.tf_processor.render(context)
            )
        return expression
