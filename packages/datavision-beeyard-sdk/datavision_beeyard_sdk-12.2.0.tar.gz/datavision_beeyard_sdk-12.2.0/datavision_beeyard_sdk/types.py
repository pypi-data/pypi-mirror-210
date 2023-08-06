""" Contains some shared types for properties """
from typing import (
    BinaryIO,
    Generic,
    MutableMapping,
    Optional,
    TextIO,
    Tuple,
    TypeVar,
    Union,
    get_type_hints,
)

import attr


class Unset:
    def __bool__(self) -> bool:
        return False


UNSET: Unset = Unset()

FileJsonType = Tuple[Optional[str], Union[BinaryIO, TextIO], Optional[str]]


@attr.s(auto_attribs=True)
class File:
    """Contains information for file uploads"""

    payload: Union[BinaryIO, TextIO]
    file_name: Optional[str] = None
    mime_type: Optional[str] = None

    def to_tuple(self) -> FileJsonType:
        """Return a tuple representation that httpx will accept for multipart/form-data"""
        return self.file_name, self.payload, self.mime_type


T = TypeVar("T")


@attr.s(auto_attribs=True)
class Response(Generic[T]):
    """A response from an endpoint"""

    status_code: int
    content: bytes
    headers: MutableMapping[str, str]
    parsed: Optional[T]


__all__ = ["File", "Response", "FileJsonType"]


def strict_types(f):
    def type_checker(*args, **kwargs):
        hints = get_type_hints(f)
        all_args = kwargs.copy()
        all_args.update(dict(zip(f.__code__.co_varnames, args)))
        for key in all_args:
            if key in hints:
                if type(all_args[key]) != hints[key]:
                    raise Exception(
                        "Type of {} is {} and not {} (serialized json object)".format(
                            key, type(all_args[key]), hints[key]
                        )
                    )
        return f(*args, **kwargs)

    return type_checker


def check_input(f):
    def input_checker(*args, **kwargs):
        fieldTypes = ["name", "mimeType", "dataType"]
        dataTypes = ["image", "document", "overlay", "file", ""]
        all_args = kwargs.copy()
        all_args.update(dict(zip(f.__code__.co_varnames, args)))
        for key in all_args:
            if key == "field" and all_args[key] not in fieldTypes:
                raise Exception(f"field must be one of {fieldTypes}")
            if key == "dataType":
                for opt in all_args[key]:
                    if opt not in dataTypes:
                        raise Exception(f"dataType must be one of {dataTypes}")
        return f(*args, **kwargs)

    return input_checker


def favorite_query_checker(f):
    def input_checker(*args, **kwargs):
        sorting_field = ["created", "modified", "uploaded"]
        sorting_direction = ["desc", "asc"]
        all_args = kwargs.copy()
        all_args.update(dict(zip(f.__code__.co_varnames, args)))
        for key in all_args:
            if key == "sorting_field" and all_args[key] not in sorting_field:
                raise Exception(f"sorting_field must be one of {sorting_field}")
            if key == "sorting_direction" and all_args[key] not in sorting_direction:
                raise Exception(f"sorting_direction must be one of {sorting_direction}")
        return f(*args, **kwargs)

    return input_checker
