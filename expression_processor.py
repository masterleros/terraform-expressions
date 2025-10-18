import re
from enum import Enum
from dataclasses import dataclass


class ExpTokenError(Exception): ...


@dataclass
class ExpFound:
    id: Enum
    value: str
    arguments: dict
    f_render: callable = None
    remaining: list = None

    def __post_init__(self):
        if self.remaining is None:
            self.remaining = []


class ExpContext:
    def __init__(self, value: str):
        self.value = value
        self.tokens = list(value.split("."))
        self.found = list[ExpFound]()
        self.embrace = ""


class ExpProcessor(list):

    exp_start = r"(?<!\.)"
    exp_word = r"[-\w]+\b"
    exp_args = r"\([-\"',\w]*\)"
    re_arg_extract = re.compile(r"(?:\(|,)([-\"'\w]*)")

    def __init__(
        self,
        id: Enum,
        exp: str = r"[-\w]+",
        last_match: bool = False,
        arguments: dict = {},
        children: list = [],
        f_found=lambda c, i: ...,
        f_render=lambda c, i: ".".join([i.value, *i.remaining]),
    ):
        if isinstance(children, ExpProcessor):
            raise ValueError("Children must be a list of ExpProcessor")
        self.extend(children)
        self.id = id
        self.exp = f"{self.exp_start}{exp}\\b(?:{self.exp_args})?"
        self.exp_extract = f"({self.exp_start}\\b{exp}\\b(?:{self.exp_args})?(?:\\.{self.exp_word}(?:{self.exp_args})?)*)"
        self.exp_help = f"{exp}" + (f"({','.join(arguments)})" if arguments else "")
        self.re_exp = re.compile(self.exp)
        self.re_exp_extract = re.compile(self.exp_extract)
        self.arguments = arguments
        self.last_match = last_match
        self.max_args = len(self.arguments)
        self.min_args = len(
            [i for i in self.arguments if self.arguments[i] is not None]
        )
        self.f_found = f_found
        self.f_render = f_render

    def __str__(self):
        if self:
            return f"'{self.exp}' > [ " + ", ".join([str(i) for i in self]) + " ]"
        return f"'{self.exp}'"

    def parse_args(self, token: str):

        # Get arguments
        arguments = self.re_arg_extract.findall(token)

        # Validate if not a function
        if self.max_args == 0 and len(arguments) > 0:
            raise ValueError(f"{self.id.value} '{token}' does not support arguments")

        # Validate count
        if not self.min_args <= len(arguments) <= self.max_args:
            raise ValueError(
                f"'{token}' expected '{len(self.arguments)}' arguments ({', '.join(self.arguments)}), found '{len(arguments)}' "
            )

        # Update found arguments
        elif self.arguments:
            return dict(zip(self.arguments, arguments))

        return None

    def parse(self, context: ExpContext, position: int = 0):

        # Process current token
        token = context.tokens[position]
        value = next(iter(self.re_exp.findall(token)), None)

        # print(
        #     f"Processing '{self.id.value}' value: '{token}' with '{self.exp}' -> {value}"
        # )
        if not value:
            return None

        # Update context
        context.found.append(
            ExpFound(
                self.id,
                value,
                self.parse_args(token),
                self.f_render,
                remaining=context.tokens[position + 1 :] if self.last_match else None,
            )
        )

        # Handle remaining values if any
        if not self.last_match and position + 1 < len(context.tokens):
            for c in self:
                if c.parse(context, position + 1) is not None:
                    return context

            # If no child could process the remaining values, raise an error
            raise ValueError(
                f"'{context.tokens[position+1]}' is not valid (expected: {' | '.join([i.exp_help for i in self])})"
            )

        # Call found handler
        self.f_found(context, context.found[position])

        return context

    def extract(self, value: str):
        return [i for i in self.re_exp_extract.findall(value)]


class ExpProcessorCollection(list):

    re_exp_extract = re.compile(r"\$\{([^\$\$\}]*)\}")

    def __init__(self, processors: list[ExpProcessor]):
        self.extend(processors)

    def extract(self, expression: str):
        extracted = []
        for e_found in self.re_exp_extract.findall(expression):
            extracted.extend([e.extract(e_found) for e in self])
        return [i for e in extracted for i in e]

    def parse(self, value: str) -> ExpContext:

        try:
            context = ExpContext(value)
            for c in self:
                if c.parse(context) is not None:
                    return context
        except Exception as e:
            raise ExpTokenError(f"Invalid '{value}': {e}")

        return None

    def render(self, context: ExpContext):
        result = ".".join(
            [s for s in [i.f_render(context, i) for i in context.found] if s]
        )
        if context.embrace:
            result = context.embrace.replace("{result}", result)
        return result

    def replace(self, expression: str, value: dict, new_value: str):
        return expression.replace(value, new_value)
