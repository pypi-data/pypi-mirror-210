from typing import Any
from abc import ABC, abstractmethod

from dataclasses import dataclass
from config_joker.utils.parser import dict_extractor, parse_list_of_dicts

from enum import Enum
from typing import Optional, Union, List, Dict


class ConfigStructure(Enum):
    DEFAULT_DICT = 1
    LIST_OF_DICTS = 2
    

@dataclass
class SourceResponse:
    exists: bool
    value: Any


class Source(ABC):
    @abstractmethod
    def get_value(self, key: str) -> SourceResponse:
        'Get the value in the source using the key'


class SourceAsDict(Source):
    def __init__(self,
                 file_path: str,
                 config_path: str = None,
                 config_scructure: Optional[ConfigStructure] = None,
                 key_name: Optional[str] = None,
                 value_name: Optional[str] = None) -> None:

        self._file_contents = self._load_from_file(file_path)
        self._config_scructure = config_scructure if config_scructure else ConfigStructure.DEFAULT_DICT
        self._data = self._extract_config(config_path=config_path, file_content=self._file_contents)
        if config_scructure == ConfigStructure.LIST_OF_DICTS:
            if not key_name: raise KeyError('missing attribte key_name')
            if not value_name: raise KeyError('missing attribte value_name')
            self._data = parse_list_of_dicts(data=self._data, k_name=key_name, v_name=value_name)

    def _extract_config(self, config_path: str, file_content: Union[List, Dict]) -> Union[List, Dict]:
        if config_path:
            return dict_extractor(path=config_path, data=file_content)
        else:
            return file_content

    def _load_from_file(self, path: str) -> dict:
        raise NotImplementedError()

    def get_value(self, key: str) -> SourceResponse:
        try:
            response = dict_extractor(path=key, data=self._data)
            return SourceResponse(
                exists=True,
                value=response
            )
        except KeyError:
            return SourceResponse(
                exists=False,
                value=None
            )