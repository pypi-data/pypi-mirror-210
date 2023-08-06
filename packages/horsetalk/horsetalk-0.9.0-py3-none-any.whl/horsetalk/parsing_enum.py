from enum import Enum, EnumMeta


class ParsingEnumMeta(EnumMeta):
    def __getitem__(cls, name):
        for member in cls.__members__:
            test_val = (
                name.strip()
                .replace("-", " ")
                .replace(" ", "_")
                .replace("'", "")
                .upper()
            )
            if member == test_val:
                return cls.__members__[member]
        raise KeyError(name)


class ParsingEnum(Enum, metaclass=ParsingEnumMeta):
    pass
