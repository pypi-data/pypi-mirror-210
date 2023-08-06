#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tomli
from pathlib import Path

from slpkg.configs import Configs
from slpkg.toml_error_message import TomlErrors


class Blacklist(Configs):
    """ Reads and returns the blacklist. """

    def __init__(self):
        super(Configs, self).__init__()

        self.errors = TomlErrors()
        self.blacklist_file_toml = Path(self.etc_path, 'blacklist.toml')

    def packages(self) -> tuple:
        """ Reads the blacklist file. """
        packages: tuple = tuple()
        if self.blacklist_file_toml.is_file():
            try:
                with open(self.blacklist_file_toml, 'rb') as black:
                    packages: tuple = tuple(tomli.load(black)['BLACKLIST']['PACKAGES'])
            except (tomli.TOMLDecodeError, KeyError) as error:
                self.errors.raise_toml_error_message(error, self.blacklist_file_toml)

        return packages
