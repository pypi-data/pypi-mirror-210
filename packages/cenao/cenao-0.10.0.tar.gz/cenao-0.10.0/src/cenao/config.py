import os
from typing import Optional, Any, Dict

import yaml
from pathlib import Path

from cenao.exceptions import ConfigNotExistsException


class Config:
    """
    Config handler and processor
    """

    def __init__(self, filename: Optional[str]):
        self.config = {}

        if filename:
            path = Path(filename)
            if not path.exists():
                raise ConfigNotExistsException(path)

            _yaml = yaml.safe_load(path.open())
            if not _yaml:
                _yaml = {}
            self.config = _yaml

    def __getitem__(self, item) -> Dict[str, Any]:
        return self.get(item)

    def get(self, item, default=None) -> Dict[str, Any]:
        """
        Returns item from config.
        :param item: Key to get from config
        :param default: Default value if key is not exists
        :return: Value of config key
        """
        return self.config.get(item, default)

    def process_env(self, env_prefix: str):
        """
        Scan environment variables and enrich config by deconstructing its path.
        Example: `APP_WEB__PORT`'s value will be written into config by path `web.port`
        :param env_prefix: prefix to filter out variables. Default is `APP`
        """
        for e in os.environ:
            if e.startswith(env_prefix):
                entry_value = os.environ.get(e)
                entry_path = e.lower().split('__')[1:]

                path = self.config
                entry_path_len = len(entry_path)
                for i in range(entry_path_len):
                    entry = entry_path[i]
                    if entry_path_len - i != 1:
                        if entry not in path:
                            path[entry] = {}
                        path = path[entry]
                    else:
                        path[entry] = entry_value
