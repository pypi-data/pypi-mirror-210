from enum import Enum


class Kind(Enum):
    COLOR = 1
    RESET = 2


class Code(Enum):
    def __init__(self, code, kind):
        self.code = code
        self.kind = kind

    red = '\033[1;31m', Kind.COLOR
    green = '\033[1;32m', Kind.COLOR
    yellow = '\033[1;33m', Kind.COLOR
    blue = '\033[1;34m', Kind.COLOR
    magenta = '\033[1;35m', Kind.COLOR
    cyan = '\033[1;36m', Kind.COLOR
    reset = '\033[0m', Kind.RESET


class ColoredString:
    def __init__(self, color):
        self.color = color
        self.values = []

    def __str__(self, depth=0):
        self_code = Code[self.color].code
        result = self_code
        total_values = len(self.values)

        for i in range(total_values):
            value = self.values[i]
            next_value = self.values[i+1] if i+1 < total_values else None
            value_is_colored_string = isinstance(value, ColoredString)

            if value_is_colored_string:
                result += value.__str__(depth=depth+1)
            else:
                result += str(value)

            if (
                next_value
                and value_is_colored_string
                and isinstance(next_value, str)
            ):
                result += self_code

        if depth == 0:
            result += Code.reset.code

        return result

    def __repr__(self):
        return f"<ColoredString color={self.color} values={self.values}>"

    def __add__(self, other):
        return str(self) + str(other)

    def __radd__(self, other):
        return str(other) + str(self)


class ColorMethod:
    def __init__(self, context, color):
        self.context = context
        self.color = color

    def __str__(self):
        return f"<ColorMethod color={self.color}>"

    def __repr__(self):
        return str(self)

    def __call__(self, *values):
        self.context.colored_string = ColoredString(self.color)

        for value in values:
            self.context.colored_string.values.append(value)

        return self.context.colored_string


class ColorContext:
    def __init__(self):
        self._define_color_methods()
        self.colored_string = None

    def _define_color_methods(self):
        for code in filter(lambda c: c.kind == Kind.COLOR, Code):
            self.__setattr__(code.name, ColorMethod(self, code.name))
