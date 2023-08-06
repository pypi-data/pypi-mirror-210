'''matchutils: extensions for python\'s match/case statement

https://github.com/thomasjlsn/matchutils
'''

import re


# HACK (this applies to all following `__eq__` methods):
#      mypy expects `other` in `__eq__()` signature to be type `object`, but we
#      need it to be type `str`. Oh well, Extra type safety is ok with me.


def _init_type_error(obj: object) -> str:
    return f'the first argument to "{obj.__class__.__name__}" must be type "str"'


def _eq_type_error(obj: object) -> str:
    return f'case arguments against "{obj.__class__.__name__}" must be type "str"'


class AsSubstring:
    def __init__(self, value: str, case_insensitive: bool = False) -> None:
        if not isinstance(value, str):
            raise TypeError(_init_type_error(self))

        self.case_insensitive: bool = case_insensitive
        self.value: str = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, str):
            raise TypeError(_eq_type_error(self))

        if self.case_insensitive:
            return self.value.casefold().__contains__(other.casefold())
        else:
            return self.value.__contains__(other)


class AsRegex:
    def __init__(self, value: str, case_insensitive: bool = False) -> None:
        if not isinstance(value, str):
            raise TypeError(_init_type_error(self))

        self.case_insensitive: bool = case_insensitive
        self.value: str = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, str):
            raise TypeError(_eq_type_error(self))

        if self.case_insensitive:
            return bool(re.search(other, self.value, flags=re.I))
        else:
            return bool(re.search(other, self.value))


# TODO Uses bash pattern matching syntax to emulate bash's version of case statements.
class AsPattern:
    def __init__(self, value: str, case_insensitive: bool = False) -> None:
        raise NotImplementedError('oops, still need to write this class...')
    #     if not isinstance(value, str):
    #         raise TypeError(_init_type_error(self))
    #
    #     self.case_insensitive: bool = case_insensitive
    #     self.value: str = value
    #
    # def __eq__(self, other: object) -> bool:
    #     if not isinstance(other, str):
    #         raise TypeError(_eq_type_error(self))
    #
    #     if self.case_insensitive:
    #         return bool(re.search(other, self.value, flags=re.I))
    #     else:
    #         return bool(re.search(other, self.value))


if __name__ == '__main__':
    # match AsSubstring(1, case_insensitive=True):
    match AsRegex('Hello world', case_insensitive=True):
        case '^h':
            print('wow')
        case 'w.rld$':
            print('hmmm')
        case _:
            print('darn')
