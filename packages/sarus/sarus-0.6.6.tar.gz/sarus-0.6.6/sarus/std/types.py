from sarus.dataspec_wrapper import DataSpecWrapper
from sarus.utils import sarus_init


class Slice(DataSpecWrapper[slice]):
    @sarus_init("std.SLICE")
    def __init__(self, *args, **kwargs) -> None:
        ...


class Set(DataSpecWrapper[set]):
    @sarus_init("std.SET")
    def __init__(self, *args, **kwargs) -> None:
        """Need to pass all arguments Set(*args)."""
        ...


class Dict(DataSpecWrapper[dict]):
    @sarus_init("std.DICT")
    def __init__(self, *args, **kwargs) -> None:
        """Need to pass all arguments Dict(**kwargs)."""
        ...


class List(DataSpecWrapper[list]):
    @sarus_init("std.LIST")
    def __init__(self, *args, **kwargs) -> None:
        """Need to pass all arguments List(*args)."""

    def __iter__(self):
        self.__sarus_idx__ = 0
        return self

    def __next__(self):
        try:
            idx = self.__sarus_idx__
            self.__sarus_idx__ += 1
            return self[idx]
        except IndexError:
            raise StopIteration


class Tuple(DataSpecWrapper[tuple]):
    @sarus_init("std.TUPLE")
    def __init__(self, *args, **kwargs) -> None:
        """Need to pass all arguments Tuple(*args)."""

    def __iter__(self):
        self.__sarus_idx__ = 0
        return self

    def __next__(self):
        try:
            idx = self.__sarus_idx__
            self.__sarus_idx__ += 1
            return self[idx]
        except IndexError:
            raise StopIteration


class Int(DataSpecWrapper[int]):
    ...


class Float(DataSpecWrapper[float]):
    ...


class String(DataSpecWrapper[str]):
    ...
