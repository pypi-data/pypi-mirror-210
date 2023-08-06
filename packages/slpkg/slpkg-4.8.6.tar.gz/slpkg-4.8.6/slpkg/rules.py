#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tomli
from pathlib import Path

from slpkg.configs import Configs
from slpkg.toml_error_message import TomlErrors


class Rules(Configs):
    """ Reads and returns the rules. """

    def __init__(self):
        super(Configs, self).__init__()

        self.errors = TomlErrors()
        self.rules_file_toml = Path(self.etc_path, 'rules.toml')

    def packages(self) -> tuple:
        """ Reads the config rules file. """
        packages: tuple = tuple()
        if self.rules_file_toml.is_file():
            try:
                with open(self.rules_file_toml, 'rb') as conf:
                    packages: tuple = tuple(tomli.load(conf)['UPGRADE']['PACKAGES'])
            except (tomli.TOMLDecodeError, KeyError) as error:
                self.errors.raise_toml_error_message(error, self.rules_file_toml)

        return packages
