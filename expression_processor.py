import re
from dataclasses import dataclass


class ExpTokenError(Exception): ...


@dataclass
class ExpFound():
    id: str
    value: str
    arguments: dict
    f_render: callable = None
    f_proccess: callable = None
    remaining: list = None


class ExpContext():
    def __init__(self, value: str):
        self.value = value
        self.tokens = list(value.split("."))
        self.found = list[ExpFound]()
        self.embrace = ""


class ExpProcessor(list):

    re_start = r"(?<!\.)"
    re_word = r"[-\w]+\b"
    re_args = r"\([-\"',\w]*\)"

    def __init__(
        self,
        id: str,
        exp: str = r"[-\w]+",
        last_match: bool = False,
        arguments: dict = {},
        children: list = [],
        f_found = lambda c, i: ...,
        f_render = lambda c, i, **k: '.'.join([ i["value"], *i.get("remaining", []) ]),
        f_process = None
    ):
        if isinstance(children, ExpProcessor):
            raise ValueError("Children must be a list of ExpProcessor")
        self.extend(children)
        self.id = id
        self.exp = f"{self.re_start}{exp}\\b(?:{self.re_args})?"
        self.exp_extract = f"({self.re_start}\\b{exp}\\b(?:{self.re_args})?(?:\\.{self.re_word}(?:{self.re_args})?)*)"
        self.exp_help = f"{exp}" + (f"({','.join(arguments)})" if arguments else "")
        self.arguments = arguments
        self.last_match = last_match
        self.max_args = len(self.arguments)
        self.min_args = len(
            [i for i in self.arguments if self.arguments[i] is not None]
        )
        self.f_found = f_found
        self.f_render = f_render
        self.f_process = f_process

    def __str__(self):
        if self:
            return f"'{self.exp}' > [ " + ", ".join([str(i) for i in self]) + " ]"
        return f"'{self.exp}'"

    def parse_args(self, token: str):

        # Get arguments
        arguments = re.findall(r"(?:\(|,)([-\"'\w]*)", token)

        # Validate if not a function
        if self.max_args == 0 and len(arguments) > 0:
            raise ValueError(f"'{token}' unexpected arguments (not a function)")

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
        value = next(iter(re.findall(self.exp, token)), None)

        # print(f"Processed '{token}' with '{self.exp}' -> {value}")
        if not value:
            return None
        
        # Update context
        context.found.append(
            ExpFound(
                self.id,
                value,
                self.parse_args(token),
                self.f_render,
                self.f_process,
                remaining = context.tokens[position + 1 :] if self.last_match else None
            )
        )
        
        # Handle remaining values if any
        if not self.last_match and position + 1 < len(context.tokens):
            for c in self:
                if c.parse(context, position + 1) is not None:
                    return context

            # If no child could process the remaining values, raise an error
            raise ValueError(
                f"'{context.tokens[position+1]}' is not a valid object (expected: {' | '.join([i.exp_help for i in self])})"
            )

        # Call found handler
        self.f_found(context, context.found[position])

        return context

    def extract(self, value: str):
        return [i for i in re.findall(self.exp_extract, value)]


class ExpProcessorCollection(list):

    def __init__(self, processors: list[ExpProcessor]):
        self.extend(processors)

    def extract(self, expression: str):
        extracted = []
        for e_found in re.findall(r"\$\{([^\$\$\}]*)\}", expression):
            extracted.extend([ e.extract(e_found) for e in self ])
        return [ i for e in extracted for i in e ]

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

    def process(self, context:ExpContext, *kargs, **kwargs):
        try:
            [s for s in [i.f_proccess(context, i, *kargs, **kwargs) for i in context.found if i.f_proccess] if s]
        except Exception as e:
            raise type(e)(f"Cannot process '{context.value}': {e}")

    def replace(self, expression:str, value:dict, new_value:str):
        return expression.replace(value, new_value)