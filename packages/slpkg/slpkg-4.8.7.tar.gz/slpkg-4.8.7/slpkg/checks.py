#!/usr/bin/python3
# -*- coding: utf-8 -*-

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.error_messages import Errors
from slpkg.repositories import Repositories
from slpkg.models.models import session as Session

from slpkg.models.models import SBoTable, PonceTable, BinariesTable


class Check(Configs):
    """ Some checks before proceed. """

    def __init__(self, repository: str):
        super(Configs, self).__init__()
        self.repository = repository

        self.errors = Errors()
        self.utils = Utilities()
        self.repos = Repositories()

        self.session = Session
        self.count_rows: int = 0
        self.is_binary: bool = self.utils.is_binary_repo(repository)

        self.sbo_table: dict = {
            self.repos.sbo_repo_name: SBoTable,
            self.repos.ponce_repo_name: PonceTable
        }

    def package_exists_in_the_database(self, packages: list, data: dict) -> None:
        not_packages: list = []

        for pkg in packages:
            if not data.get(pkg) and pkg != '*':
                not_packages.append(pkg)

        if not_packages:
            self.errors.raise_error_message(f"Packages '{', '.join(not_packages)}' does not exists",
                                            exit_status=1)

    def is_package_unsupported(self, slackbuilds: list, data: dict) -> None:
        """ Checking for unsupported slackbuilds. """
        for sbo in slackbuilds:
            if sbo != '*':
                if self.os_arch == 'x86_64' and data[sbo]['download64']:
                    sources: list = data[sbo]['download64'].split()
                else:
                    sources: list = data[sbo]['download'].split()

                if 'UNSUPPORTED' in sources:
                    self.errors.raise_error_message(f"Package '{sbo}' unsupported by arch",
                                                    exit_status=1)

    def is_package_installed(self, packages: list) -> None:
        """ Checking for installed packages. """
        not_found: list = []

        for pkg in packages:
            if not self.utils.is_package_installed(pkg):
                not_found.append(pkg)

        if not_found:
            self.errors.raise_error_message(f'Not found \'{", ".join(not_found)}\' installed packages',
                                            exit_status=1)

    def is_database_empty(self) -> None:
        """ Checking for empty table and database file. """
        if self.repository == '*':
            self.count_of_repositories()
        else:
            self.count_of_repository()

        if self.count_rows == 0:
            self.errors.raise_error_message("You need to update the package lists first, run:\n\n"
                                            f"{'':>14}$ slpkg update", exit_status=1)

    def count_of_repositories(self) -> None:
        for repository, item in self.repos.repositories.items():
            if item['path'] and item['enable']:
                if self.utils.is_binary_repo(repository):
                    self.count_rows += self.session.query(BinariesTable.id).where(
                        BinariesTable.repo == repository).count()
                else:
                    self.count_rows += self.session.query(self.sbo_table[repository].id).count()

    def count_of_repository(self) -> None:
        if self.is_binary:
            self.count_rows: int = self.session.query(
                BinariesTable.id).where(BinariesTable.repo == self.repository).count()
        else:
            self.count_rows: int = self.session.query(self.sbo_table[self.repository].id).count()
