from typing import Iterable, List, Optional, Union

from pydantic import BaseModel, Field

from ids_validator.checks.rules_checker import BackwardCompatibleType

_RELATED_FILES = "root.properties.related_files"
_RELATED_FILES_ITEMS = "root.properties.related_files.items"
_RELATED_FILES_NAME = f"{_RELATED_FILES_ITEMS}.properties.name"
_RELATED_FILES_PATH = f"{_RELATED_FILES_ITEMS}.properties.path"
_RELATED_FILES_SIZE = f"{_RELATED_FILES_ITEMS}.properties.size"
_CHECKSUM = f"{_RELATED_FILES_ITEMS}.properties.checksum"
_CHECKSUM_VALUE = f"{_CHECKSUM}.properties.value"
_CHECKSUM_ALGORITHM = f"{_CHECKSUM}.properties.algorithm"

_POINTER = f"{_RELATED_FILES_ITEMS}.properties.pointer"
_POINTER_FILE_KEY = f"{_POINTER}.properties.fileKey"
_POINTER_VERSION = f"{_POINTER}.properties.version"
_POINTER_BUCKET = f"{_POINTER}.properties.bucket"
_POINTER_TYPE = f"{_POINTER}.properties.type"
_POINTER_FILE_ID = f"{_POINTER}.properties.fileId"


class Checks(BaseModel):
    type_: Union[None, str, List[str]] = Field(alias="type")
    compatible_type: Optional[List[BackwardCompatibleType]]
    required: Optional[Iterable[str]]
    properties: Optional[Iterable[str]]
    min_properties: Optional[Iterable[str]]
    min_required: Optional[Iterable[str]]


_RULES = {
    _RELATED_FILES: Checks(type_="array"),
    _RELATED_FILES_ITEMS: Checks(
        type_="object",
        min_properties=["name", "path", "size", "checksum", "pointer"],
        min_required=["pointer"],
    ),
    _RELATED_FILES_NAME: Checks(type_=["null", "string"]),
    _RELATED_FILES_PATH: Checks(type_=["null", "string"]),
    _CHECKSUM: Checks(
        type_="object",
        min_properties=["value", "algorithm"],
        min_required=["value", "algorithm"],
    ),
    _CHECKSUM_VALUE: Checks(type_=["string"]),
    _CHECKSUM_ALGORITHM: Checks(type_=["string", "null"]),
    _POINTER: Checks(
        type_="object",
        min_properties=["fileKey", "version", "bucket", "type", "fileId"],
        min_required=["fileKey", "version", "bucket", "type", "fileId"],
    ),
    _POINTER_FILE_KEY: Checks(type_="string"),
    _POINTER_VERSION: Checks(type_="string"),
    _POINTER_BUCKET: Checks(type_="string"),
    _POINTER_TYPE: Checks(type_="string"),
    _POINTER_FILE_ID: Checks(type_="string"),
}

RULES = {
    field: checks.dict(by_alias=True, exclude_none=True)
    for field, checks in _RULES.items()
}
