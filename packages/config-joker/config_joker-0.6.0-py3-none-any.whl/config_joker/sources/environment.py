import os

from config_joker.sources.source import Source, SourceResponse


class EnvironmentSource(Source):
    def get_value(self, key: str) -> SourceResponse:
        try:
            return SourceResponse(
                exists=True,
                value=os.environ[key]
            )
        except KeyError:
            return SourceResponse(
                exists=False,
                value=None
            )
