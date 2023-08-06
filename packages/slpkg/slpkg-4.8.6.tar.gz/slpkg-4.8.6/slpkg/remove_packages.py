#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.dialog_box import DialogBox
from slpkg.views.views import ViewMessage
from slpkg.views.asciibox import AsciiBox
from slpkg.multi_process import MultiProcess
from slpkg.models.models import LogsDependencies
from slpkg.models.models import session as Session


class RemovePackages(Configs):
    """ Removes installed packages with dependencies if they installed with
        slpkg install command.
    """

    def __init__(self, packages: list, flags: list):
        super(Configs, self).__init__()
        self.packages: list = packages

        self.session = Session
        self.dialogbox = DialogBox()
        self.utils = Utilities()
        self.ascii = AsciiBox()
        self.multi_proc = MultiProcess(flags)
        self.view = ViewMessage(flags)

        self.logs_dependencies: dict = {}
        self.packages_for_remove: list = []
        self.installed_dependencies: list = []
        self.dependencies: list = []
        self.llc: str = self.ascii.lower_left_corner
        self.hl: str = self.ascii.horizontal_line

        self.option_for_resolve_off: bool = self.utils.is_option(
            ('-O', '--resolve-off'), flags)

        self.option_for_yes: bool = self.utils.is_option(
            ('-y', '--yes'), flags)

    def remove(self) -> None:
        self.query_logs_dependencies()
        self.add_packages_for_remove()
        self.save_dependencies_for_remove()
        self.remove_doubles_dependencies()
        self.remove_doubles_installed_dependencies()
        self.choose_dependencies_for_remove()
        self.update_installed_dependencies_for_remove()
        self.add_installed_dependencies_to_remove()

        self.view.remove_packages(self.packages, self.dependencies)
        self.view.question()

        start: float = time.time()
        self.remove_packages()
        elapsed_time: float = time.time() - start
        self.utils.finished_time(elapsed_time)

    def add_packages_for_remove(self) -> None:
        for package in self.packages:
            installed: str = self.utils.is_package_installed(package)
            if installed:
                self.packages_for_remove.append(installed)

    def save_dependencies_for_remove(self) -> None:
        if not self.option_for_resolve_off:
            for package in self.packages:
                if self.logs_dependencies.get(package):
                    requires: tuple = self.logs_dependencies[package]

                    for require in requires:
                        installed: str = self.utils.is_package_installed(require)
                        if installed and require not in self.packages:
                            self.dependencies.append(require)

    def remove_doubles_dependencies(self) -> None:
        self.dependencies: list = list(set(self.dependencies))

    def remove_doubles_installed_dependencies(self) -> None:
        self.installed_dependencies: list = list(set(self.installed_dependencies))

    def update_installed_dependencies_for_remove(self) -> None:
        for dependency in self.dependencies:
            installed: str = self.utils.is_package_installed(dependency)
            if installed and dependency not in self.packages:
                self.installed_dependencies.append(installed)

    def add_installed_dependencies_to_remove(self) -> None:
        self.packages_for_remove.extend(self.installed_dependencies)

    def remove_packages(self) -> None:
        print(f'Started of removing total ({self.cyan}{len(self.packages_for_remove)}{self.endc}) packages:\n')
        for package in self.packages_for_remove:
            command: str = f'{self.removepkg} {package}'
            name: str = self.utils.split_package(package)['name']
            progress_message: str = f'{self.bold}{self.red}Removing{self.endc}'

            dependencies: list = self.is_dependency(name)
            if dependencies:
                self.view_warning_message(dependencies, name)
                if not self.question_to_remove():
                    continue

            self.multi_proc.process(command, package, progress_message)
            self.delete_package_from_logs(name)

    def is_dependency(self, name: str) -> list:
        dependencies: list = []
        for package, requires in self.logs_dependencies.items():
            if name in requires and package not in self.packages:
                dependencies.append(package)

        if dependencies:
            return dependencies

    def question_to_remove(self) -> bool:
        if not self.option_for_yes and self.ask_question:
            answer: str = input(f'\nDo you want to remove? [y/N] ')
            if answer in ['Y', 'y']:
                print()
                return True
            print()

    def view_warning_message(self, dependencies: list, name: str) -> None:
        print(f"\n{'':>2}{self.bold}{self.bred}{self.ascii.bullet} {name}{self.endc}: is a dependency in the packages:")
        print(f"{'':>5}{self.llc}{self.hl}", end='')
        for i, dependency in enumerate(dependencies, start=1):
            if i == 1:
                print(f"{'':>1}{self.cyan}{dependency}{self.endc}")
            if i > 1:
                print(f"{'':>8}{self.cyan}{dependency}{self.endc}")

    def query_logs_dependencies(self) -> None:
        package_requires: tuple = self.session.query(
            LogsDependencies.name, LogsDependencies.requires).all()
        for package in package_requires:
            self.logs_dependencies[package[0]] = package[1].split()

    def delete_package_from_logs(self, package) -> None:
        if not self.option_for_resolve_off:
            self.session.query(LogsDependencies).filter(
                LogsDependencies.name == package).delete()
            self.session.commit()

    def choose_dependencies_for_remove(self) -> None:
        if self.dependencies:
            height: int = 10
            width: int = 70
            list_height: int = 0
            choices: list = []
            title: str = " Choose dependencies you want to remove "

            for package in self.dependencies:
                installed_package: str = self.utils.is_package_installed(package)
                installed_version: str = self.utils.split_package(installed_package)['version']
                choices.extend([(package, installed_version, True, f'Package: {installed_package}')])

            text: str = f'There are {len(choices)} dependencies:'
            code, self.dependencies = self.dialogbox.checklist(text, self.dependencies, title, height,
                                                               width, list_height, choices)
            os.system('clear')
