#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pathlib import Path

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.repositories import Repositories


class ViewPackage(Configs):
    """ View the repository packages. """

    def __init__(self, flags: list, repository: str):
        super(Configs, self).__init__()
        self.flags: list = flags
        self.repository: str = repository

        self.utils = Utilities()
        self.repos = Repositories()

        self.repository_packages: tuple = ()
        self.readme: list = []
        self.info_file: list = []
        self.repo_build_tag: str = str()
        self.mirror: str = str()
        self.homepage: str = str()
        self.maintainer: str = str()
        self.email: str = str()
        self.dependencies: str = str()
        self.repo_tar_suffix: str = str()

        self.option_for_pkg_version: bool = self.utils.is_option(
            ('-p', '--pkg-version'), flags)

    def slackbuild(self, data: dict, slackbuilds: list) -> None:
        """ View slackbuild packages information. """
        repo: dict = {
            self.repos.sbo_repo_name: self.repos.sbo_repo_tar_suffix,
            self.repos.ponce_repo_name: str()
        }
        self.repo_tar_suffix: str = repo[self.repository]
        self.repository_packages: tuple = tuple(data.keys())

        for sbo in slackbuilds:
            for name, item in data.items():

                if sbo == name or sbo == '*':
                    path_file: Path = Path(self.repos.repositories[self.repository]['path'],
                                           item['location'], name, 'README')
                    path_info: Path = Path(self.repos.repositories[self.repository]['path'],
                                           item['location'], name, f'{name}.info')

                    self.read_the_readme_file(path_file)
                    self.read_the_info_file(path_info)
                    self.read_repo_build_tag(name, item)
                    self.assign_the_sbo_mirror()
                    self.assign_the_info_file_variables()
                    self.assign_dependencies(item)
                    self.assign_dependencies_with_version(item, data)
                    self.view_slackbuild_package(name, item)

    def read_the_readme_file(self, path_file: Path) -> None:
        self.readme: list = self.utils.read_text_file(path_file)

    def read_the_info_file(self, path_info: Path) -> None:
        self.info_file: list = self.utils.read_text_file(path_info)

    def read_repo_build_tag(self, name: str, item: dict) -> None:
        self.repo_build_tag: str = self.utils.read_slackbuild_build_tag(
             name, item['location'], self.repository)

    def assign_the_sbo_mirror(self) -> None:
        self.mirror: str = self.repos.repositories[self.repository]['mirror'][0]

    def assign_the_info_file_variables(self) -> None:
        for line in self.info_file:
            if line.startswith('HOMEPAGE'):
                self.homepage: str = line[10:-2].strip()
            if line.startswith('MAINTAINER'):
                self.maintainer: str = line[12:-2].strip()
            if line.startswith('EMAIL'):
                self.email: str = line[7:-2].strip()

    def assign_dependencies(self, item: dict) -> None:
        self.dependencies: str = (', '.join([f'{self.cyan}{pkg}' for pkg in item['requires'].split()]))

    def assign_dependencies_with_version(self, item: dict, data: dict) -> None:
        if self.option_for_pkg_version:
            self.dependencies: str = (', '.join(
                [f"{self.cyan}{pkg}{self.endc}-{self.yellow}{data[pkg]['version']}"
                 f"{self.green}" for pkg in item['requires'].split()
                 if pkg in self.repository_packages]))

    def view_slackbuild_package(self, name: str, item: dict) -> None:
        print(f"Name: {self.green}{name}{self.endc}\n"
              f"Version: {self.green}{item['version']}{self.endc}\n"
              f"Build: {self.green}{self.repo_build_tag}{self.endc}\n"
              f"Requires: {self.green}{self.dependencies}{self.endc}\n"
              f"Homepage: {self.blue}{self.homepage}{self.endc}\n"
              f"Download SlackBuild: {self.blue}{self.mirror}"
              f"{item['location']}/{name}{self.repo_tar_suffix}{self.endc}\n"
              f"Download sources: {self.blue}{item['download']}{self.endc}\n"
              f"Download_x86_64 sources: {self.blue}{item['download64']}{self.endc}\n"
              f"Md5sum: {self.yellow}{item['md5sum']}{self.endc}\n"
              f"Md5sum_x86_64: {self.yellow}{item['md5sum64']}{self.endc}\n"
              f"Files: {self.green}{item['files']}{self.endc}\n"
              f"Description: {self.green}{item['description']}{self.endc}\n"
              f"Category: {self.red}{item['location']}{self.endc}\n"
              f"SBo url: {self.blue}{self.mirror}{item['location']}/{name}{self.endc}\n"
              f"Maintainer: {self.yellow}{self.maintainer}{self.endc}\n"
              f"Email: {self.yellow}{self.email}{self.endc}\n"
              f"\nREADME: {self.cyan}{''.join(self.readme)}{self.endc}")

    def package(self, data: dict, packages: list) -> None:
        """ View binary packages information. """
        self.repository_packages: tuple = tuple(data.keys())
        for package in packages:
            for name, item in data.items():
                if package == name or package == '*':

                    self.assign_dependencies(item)
                    self.assign_dependencies_with_version(item, data)
                    self.view_binary_package(name, item)

    def view_binary_package(self, name: str, item: dict) -> None:
        print(f"Name: {self.green}{name}{self.endc}\n"
              f"Version: {self.green}{item['version']}{self.endc}\n"
              f"Package: {self.cyan}{item['package']}{self.endc}\n"
              f"Download: {self.blue}{item['mirror']}{item['location']}/{item['package']}{self.endc}\n"
              f"Md5sum: {item['checksum']}\n"
              f"Mirror: {self.blue}{item['mirror']}{self.endc}\n"
              f"Location: {self.red}{item['location']}{self.endc}\n"
              f"Size Comp: {self.yellow}{item['size_comp']} KB{self.endc}\n"
              f"Size Uncomp: {self.yellow}{item['size_uncomp']} KB{self.endc}\n"
              f"Requires: {self.green}{self.dependencies}{self.endc}\n"
              f"Conflicts: {item['conflicts']}\n"
              f"Suggests: {item['suggests']}\n"
              f"Description: {item['description']}\n")
