from yaml import safe_load

from config_joker.sources.source import SourceAsDict


class YamlFileSource(SourceAsDict):
    def __init__(self, file_path: str, config_path: str = None, **kwargs: dict) -> None:
        super().__init__(file_path, config_path, **kwargs)

    def _load_from_file(self, path: str) -> dict:
        with open(path) as f:
            return safe_load(f)
