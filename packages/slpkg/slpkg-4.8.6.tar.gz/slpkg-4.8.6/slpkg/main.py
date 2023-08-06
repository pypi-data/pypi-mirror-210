#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from pathlib import Path

from slpkg.checks import Check
from slpkg.upgrade import Upgrade
from slpkg.configs import Configs
from slpkg.tracking import Tracking
from slpkg.repo_info import RepoInfo
from slpkg.dependees import Dependees
from slpkg.utilities import Utilities
from slpkg.cleanings import Cleanings
from slpkg.search import SearchPackage
from slpkg.views.cli_menu import Usage
from slpkg.dialog_box import DialogBox
from slpkg.views.version import Version
from slpkg.sbos.queries import SBoQueries
from slpkg.views.help_commands import Help
from slpkg.repositories import Repositories
from slpkg.binaries.install import Packages
from slpkg.dialog_configs import FormConfigs
from slpkg.check_updates import CheckUpdates
from slpkg.download_only import DownloadOnly
from slpkg.sbos.slackbuild import Slackbuilds
from slpkg.binaries.queries import BinQueries
from slpkg.logging_config import LoggingConfig
from slpkg.find_installed import FindInstalled
from slpkg.views.view_package import ViewPackage
from slpkg.remove_packages import RemovePackages
from slpkg.update_repository import UpdateRepository


class Menu(Configs):

    def __init__(self, args: list):
        super(Configs).__init__()
        self.args: list = args
        self.flags: list = []
        self.directory: Path = self.tmp_slpkg

        self.utils = Utilities()
        self.usage = Usage()
        self.repos = Repositories()

        self.repository: str = self.repos.default_repository

        self.data: dict = {}
        self.flag_yes: str = '--yes'
        self.flag_short_yes: str = '-y'
        self.flag_jobs: str = '--jobs'
        self.flag_short_jobs: str = '-j'
        self.flag_resolve_off: str = '--resolve-off'
        self.flag_short_resolve_off: str = '-O'
        self.flag_reinstall: str = '--reinstall'
        self.flag_short_reinstall: str = '-r'
        self.flag_skip_installed: str = '--skip-installed'
        self.flag_short_skip_installed: str = '-k'
        self.flag_install_data: str = '--install-data'
        self.flag_short_install_data: str = '-a'
        self.flag_full_reverse: str = '--full-reverse'
        self.flag_short_full_reverse: str = '-E'
        self.flag_search: str = '--search'
        self.flag_short_search: str = '-S'
        self.flag_no_silent: str = '--no-silent'
        self.flag_short_no_silent: str = '-n'
        self.flag_pkg_version: str = '--pkg-version'
        self.flag_short_pkg_version: str = '-p'
        self.flag_parallel: str = '--parallel'
        self.flag_short_parallel: str = '-P'
        self.flag_no_case: str = '--no-case'
        self.flag_short_no_case: str = '-m'
        self.flag_repository: str = '--repository='
        self.flag_short_repository: str = '-o'
        self.flag_directory: str = '--directory='
        self.flag_short_directory: str = '-z'

        self.flag_searches: tuple = (
            self.flag_short_search,
            self.flag_search
        )

        self.flag_no_cases: tuple = (
            self.flag_no_case,
            self.flag_short_no_case
        )

        self.options: tuple = (
            self.flag_yes,
            self.flag_short_yes,
            self.flag_jobs,
            self.flag_short_jobs,
            self.flag_resolve_off,
            self.flag_short_resolve_off,
            self.flag_reinstall,
            self.flag_short_reinstall,
            self.flag_skip_installed,
            self.flag_short_skip_installed,
            self.flag_install_data,
            self.flag_short_install_data,
            self.flag_full_reverse,
            self.flag_short_full_reverse,
            self.flag_search,
            self.flag_short_search,
            self.flag_no_silent,
            self.flag_short_no_silent,
            self.flag_pkg_version,
            self.flag_short_pkg_version,
            self.flag_parallel,
            self.flag_short_parallel,
            self.flag_no_case,
            self.flag_short_no_case,
            self.flag_repository,
            self.flag_short_repository,
            self.flag_directory,
            self.flag_short_directory,
        )

        self.commands: dict = {
            '--help': [],
            '--version': [],
            'help': [],
            'update': [
                self.flag_yes,
                self.flag_short_yes,
                self.flag_install_data,
                self.flag_short_install_data,
                self.flag_repository,
                self.flag_short_repository,
                self.flag_parallel,
                self.flag_short_parallel
            ],
            'upgrade': [
                self.flag_yes,
                self.flag_short_yes,
                self.flag_jobs,
                self.flag_short_jobs,
                self.flag_resolve_off,
                self.flag_short_resolve_off,
                self.flag_reinstall,
                self.flag_short_reinstall,
                self.flag_no_silent,
                self.flag_short_no_silent,
                self.flag_repository,
                self.flag_short_repository,
                self.flag_parallel,
                self.flag_short_parallel
            ],
            'check-updates': [
                self.flag_repository,
                self.flag_short_repository
            ],
            'repo-info': [
                self.flag_repository,
                self.flag_short_repository
            ],
            'configs': [],
            'clean-logs': [],
            'clean-data': [],
            'clean-tmp': [],
            'build': [
                self.flag_yes,
                self.flag_short_yes,
                self.flag_jobs,
                self.flag_short_jobs,
                self.flag_resolve_off,
                self.flag_short_resolve_off,
                self.flag_search,
                self.flag_short_search,
                self.flag_no_silent,
                self.flag_short_no_silent,
                self.flag_repository,
                self.flag_short_repository,
                self.flag_parallel,
                self.flag_short_parallel,
                self.flag_no_case,
                self.flag_short_no_case
            ],
            'install': [
                self.flag_yes,
                self.flag_short_yes,
                self.flag_jobs,
                self.flag_short_jobs,
                self.flag_resolve_off,
                self.flag_short_resolve_off,
                self.flag_reinstall,
                self.flag_short_reinstall,
                self.flag_skip_installed,
                self.flag_short_skip_installed,
                self.flag_search,
                self.flag_short_search,
                self.flag_no_silent,
                self.flag_short_no_silent,
                self.flag_repository,
                self.flag_short_repository,
                self.flag_parallel,
                self.flag_short_parallel,
                self.flag_no_case,
                self.flag_short_no_case
            ],
            'download': [
                self.flag_yes,
                self.flag_short_yes,
                self.flag_search,
                self.flag_short_search,
                self.flag_directory,
                self.flag_short_directory,
                self.flag_repository,
                self.flag_short_repository,
                self.flag_parallel,
                self.flag_short_parallel,
                self.flag_no_case,
                self.flag_short_no_case
            ],
            'remove': [
                self.flag_yes,
                self.flag_short_yes,
                self.flag_resolve_off,
                self.flag_short_resolve_off,
                self.flag_search,
                self.flag_short_search,
                self.flag_no_silent,
                self.flag_short_no_silent,
            ],
            'find': [
                self.flag_search,
                self.flag_short_search,
                self.flag_no_case,
                self.flag_short_no_case
            ],
            'view': [
                self.flag_search,
                self.flag_short_search,
                self.flag_repository,
                self.flag_short_repository,
                self.flag_pkg_version,
                self.flag_short_pkg_version,
                self.flag_no_case,
                self.flag_short_no_case
            ],
            'search': [
                self.flag_search,
                self.flag_short_search,
                self.flag_repository,
                self.flag_short_repository,
                self.flag_no_case,
                self.flag_short_no_case
            ],
            'dependees': [
                self.flag_full_reverse,
                self.flag_short_full_reverse,
                self.flag_search,
                self.flag_short_search,
                self.flag_repository,
                self.flag_short_repository,
                self.flag_pkg_version,
                self.flag_short_pkg_version,
                self.flag_no_case,
                self.flag_short_no_case
            ],
            'tracking': [
                self.flag_search,
                self.flag_short_search,
                self.flag_pkg_version,
                self.flag_short_pkg_version,
                self.flag_repository,
                self.flag_short_repository,
                self.flag_no_case,
                self.flag_short_no_case
            ]
        }

        self.commands['-h'] = self.commands['--help']
        self.commands['-v'] = self.commands['--version']
        self.commands['-u'] = self.commands['update']
        self.commands['-U'] = self.commands['upgrade']
        self.commands['-c'] = self.commands['check-updates']
        self.commands['-I'] = self.commands['repo-info']
        self.commands['-g'] = self.commands['configs']
        self.commands['-L'] = self.commands['clean-logs']
        self.commands['-D'] = self.commands['clean-tmp']
        self.commands['-T'] = self.commands['clean-data']
        self.commands['-b'] = self.commands['build']
        self.commands['-i'] = self.commands['install']
        self.commands['-d'] = self.commands['download']
        self.commands['-R'] = self.commands['remove']
        self.commands['-f'] = self.commands['find']
        self.commands['-w'] = self.commands['view']
        self.commands['-s'] = self.commands['search']
        self.commands['-e'] = self.commands['dependees']
        self.commands['-t'] = self.commands['tracking']

        self.split_options()
        self.split_options_from_args()
        self.move_options()
        self.invalid_options()
        self.check_for_repositories()

        self.is_binary: bool = self.utils.is_binary_repo(self.repository)
        self.check = Check(self.repository)
        self.choose = ChoosePackages(self.repository)

        logging.basicConfig(filename=LoggingConfig.log_file,
                            filemode=LoggingConfig.filemode,
                            encoding=LoggingConfig.encoding,
                            level=LoggingConfig.level)

        logger = logging.getLogger(LoggingConfig.date_time)
        logger.info(f'{self.__class__.__name__}: '
                    f'{self.__class__.__init__.__name__}: '
                    f'{args=}, {self.flags=}, {self.repository=}')

    def load_database(self):
        if self.repository != '*' and not self.data:
            if self.is_binary:
                self.data: dict = BinQueries(self.repository).repository_data()
            else:
                self.data: dict = SBoQueries(self.repository).repository_data()

    def check_for_repositories(self) -> None:
        """ Checks combination for binaries use repositories only and if repository exists. """
        except_options: tuple = (
            '-s', 'search',
        )
        if self.repository == '*' and not self.utils.is_option(except_options, self.args):
            self.usage.help_minimal(f"{self.prog_name}: invalid repository '{self.repository}'")

        elif self.repository not in list(self.repos.repositories.keys()) and self.repository != '*':
            self.usage.help_minimal(f"{self.prog_name}: invalid repository '{self.repository}'")

        if self.repository != '*':
            if not self.repos.repositories[self.repository]['enable']:
                self.usage.help_minimal(f"{self.prog_name}: repository '{self.repository}' is disabled")

    def invalid_options(self) -> None:
        """ Checks for invalid options. """
        invalid, commands, repeat = [], [], []

        for arg in self.args:
            if arg[0] == '-' and arg in self.commands.keys():
                commands.append(arg)
            elif arg[0] == '-' and arg not in self.options:
                invalid.append(arg)

        # Counts the recurring options.
        for opt in self.flags:
            if self.flags.count(opt) > 1:
                repeat.append(opt)

        # Fixed for recurring options.
        if repeat:
            self.usage.help_minimal(f"{self.prog_name}: invalid recurring options '{', '.join(repeat)}'")

        # Fixed for invalid commands combination.
        if len(commands) > 1:
            self.usage.help_minimal(f"{self.prog_name}: invalid commands combination '{', '.join(commands)}'")

        # Fixed for correct options by command.
        try:
            options: list = self.commands[self.args[0]]
            for opt in self.flags:
                if opt not in options:
                    invalid.append(opt)
        except (KeyError, IndexError):
            self.usage.help_short(1)

        # Prints error for invalid options.
        if invalid:
            self.usage.help_minimal(f"{self.prog_name}: invalid options '{','.join(invalid)}'")

    def split_options(self) -> None:
        """ Split options and commands, like: -iyjR

            slpkg -jyiR package

            Puts the command first and options after.
            Result: ['-i', '-y', '-j', '-R']
        """
        for args in self.args:
            if args[0] == '-' and args[:2] != '--' and len(args) >= 3 and '=' not in args:
                self.args.remove(args)

                for opt in list(map(lambda x: f'-{x}', [arg for arg in list(args[1:])])):
                    if opt in self.commands.keys():
                        self.args.insert(0, opt)
                        continue

                    self.args.append(opt)

    def split_options_from_args(self) -> None:
        """ Split options from arguments.

            slpkg -d package --directory=/path/to/download

            Splits the option ['--directory'] and ['/path/to/download/']
        """
        for arg in self.args:

            if arg.startswith(self.flag_directory):
                self.directory: str = arg.split('=')[1]
                self.args.remove(arg)
                self.args.append(self.flag_directory)
                break

            try:
                if arg.startswith(self.flag_short_directory):
                    self.directory: str = self.args[self.args.index(arg) + 1]
                    self.args.remove(self.directory)
                    break
            except IndexError:
                self.directory: Path = self.tmp_slpkg

            if arg.startswith(self.flag_repository):
                self.repository: str = arg.split('=')[1]
                self.args.remove(arg)
                self.args.append(self.flag_repository)
                break

            try:
                if arg.startswith(self.flag_short_repository):
                    self.repository: str = self.args[self.args.index(arg) + 1]
                    self.args.remove(self.repository)
                    break
            except IndexError:
                self.repository: str = str()

    def move_options(self) -> None:
        """ Move options to the flags and removes from the arguments. """
        new_args: list = []

        for arg in self.args:
            if arg in self.options:
                self.flags.append(arg)
            else:
                new_args.append(arg)

        self.args: list = new_args

    def is_file_list_packages(self) -> list:
        """ Checks if the arg is filelist.pkgs. """
        if self.args[1].endswith(self.file_list_suffix):
            file = Path(self.args[1])
            packages: list = list(self.utils.read_packages_from_file(file))
        else:
            packages: list = list(set(self.args[1:]))

        return packages

    def update(self) -> None:
        if len(self.args) == 1:
            update = UpdateRepository(self.flags, self.repository)
            update.repositories()
            raise SystemExit()
        self.usage.help_short(1)

    def upgrade(self) -> None:
        command: str = Menu.upgrade.__name__

        if len(self.args) == 1:
            self.load_database()
            self.check.is_database_empty()

            upgrade = Upgrade(self.repository, self.data)
            packages: list = list(upgrade.packages())

            packages: list = self.choose.packages(self.data, packages, command)

            if not packages:
                print('\nEverything is up-to-date!\n')
                raise SystemExit()

            if self.is_binary:
                install = Packages(
                    self.repository, self.data, packages, self.flags, mode=command
                )
            else:
                install = Slackbuilds(
                    self.repository, self.data, packages, self.flags, mode=command
                )

            install.execute()
            raise SystemExit()
        self.usage.help_short(1)

    def check_updates(self) -> None:
        if len(self.args) == 1:
            check = CheckUpdates(self.flags, self.repository)
            check.updates()
            raise SystemExit()
        self.usage.help_short(1)

    def repo_info(self) -> None:
        if len(self.args) == 1:
            repo = RepoInfo(self.flags, self.repository)
            repo.info()
            raise SystemExit()
        self.usage.help_short(1)

    def build(self) -> None:
        command: str = Menu.build.__name__

        if len(self.args) >= 2:
            self.load_database()
            self.check.is_database_empty()
            packages: list = self.is_file_list_packages()

            if self.utils.is_option(self.flag_no_cases, self.flags) or not self.case_sensitive:
                packages: list = self.utils.case_insensitive_pattern_matching(packages, self.data)

            if self.utils.is_option(self.flag_searches, self.flags):
                packages: list = self.choose.packages(self.data, packages, command)

            self.check.package_exists_in_the_database(packages, self.data)
            self.check.is_package_unsupported(packages, self.data)

            if self.repository in list(self.repos.repositories.keys())[:2]:
                build = Slackbuilds(
                    self.repository, self.data, packages, self.flags, mode=command
                )
                build.execute()
            else:
                self.usage.help_minimal(f"{self.prog_name}: invalid repository '{self.repository}'")

            raise SystemExit()
        self.usage.help_short(1)

    def install(self) -> None:
        command: str = Menu.install.__name__

        if len(self.args) >= 2:
            self.load_database()
            self.check.is_database_empty()
            packages: list = self.is_file_list_packages()

            if self.utils.is_option(self.flag_no_cases, self.flags) or not self.case_sensitive:
                packages: list = self.utils.case_insensitive_pattern_matching(packages, self.data)

            if self.utils.is_option(self.flag_searches, self.flags):
                packages: list = self.choose.packages(self.data, packages, command)

            self.check.package_exists_in_the_database(packages, self.data)

            if self.is_binary:
                install = Packages(self.repository, self.data, packages, self.flags, mode=command)
                install.execute()
            else:
                self.check.is_package_unsupported(packages, self.data)
                install = Slackbuilds(self.repository, self.data, packages, self.flags, mode=command)
                install.execute()
            raise SystemExit()
        self.usage.help_short(1)

    def download(self) -> None:
        command: str = Menu.download.__name__

        if len(self.args) >= 2:
            self.load_database()
            self.check.is_database_empty()
            packages: list = self.is_file_list_packages()

            if self.utils.is_option(self.flag_no_cases, self.flags) or not self.case_sensitive:
                packages: list = self.utils.case_insensitive_pattern_matching(packages, self.data)

            if self.utils.is_option(self.flag_searches, self.flags):
                packages: list = self.choose.packages(self.data, packages, command)

            self.check.package_exists_in_the_database(packages, self.data)
            down_only = DownloadOnly(self.directory, self.flags, self.data, self.repository)
            down_only.packages(packages)
            raise SystemExit()
        self.usage.help_short(1)

    def remove(self) -> None:
        command: str = Menu.remove.__name__

        if len(self.args) >= 2:
            packages: list = self.is_file_list_packages()

            if self.utils.is_option(self.flag_searches, self.flags):
                packages: list = self.choose.packages(self.data, packages, command)

            self.check.is_package_installed(packages)

            remove = RemovePackages(packages, self.flags)
            remove.remove()
            raise SystemExit()
        self.usage.help_short(1)

    def find(self) -> None:
        command: str = Menu.find.__name__

        if len(self.args) >= 2:
            self.check.is_database_empty()
            packages: list = self.is_file_list_packages()

            if self.utils.is_option(self.flag_no_cases, self.flags) or not self.case_sensitive:
                self.load_database()
                packages: list = self.utils.case_insensitive_pattern_matching(packages, self.data)

            if self.utils.is_option(self.flag_searches, self.flags):
                self.load_database()
                packages: list = self.choose.packages(self.data, packages, command)

            find = FindInstalled(self.flags, packages)
            find.find()
            raise SystemExit()
        self.usage.help_short(1)

    def view(self) -> None:
        command: str = Menu.view.__name__

        if len(self.args) >= 2:
            self.load_database()
            self.check.is_database_empty()
            packages: list = self.is_file_list_packages()

            if self.utils.is_option(self.flag_no_cases, self.flags) or not self.case_sensitive:
                packages: list = self.utils.case_insensitive_pattern_matching(packages, self.data)

            if self.utils.is_option(self.flag_searches, self.flags):
                packages: list = self.choose.packages(self.data, packages, command)

            self.check.package_exists_in_the_database(packages, self.data)

            view = ViewPackage(self.flags, self.repository)

            if self.is_binary:
                view.package(self.data, packages)
            else:
                view.slackbuild(self.data, packages)
            raise SystemExit()
        self.usage.help_short(1)

    def search(self) -> None:
        command: str = Menu.search.__name__

        if len(self.args) >= 2:
            self.check.is_database_empty()
            packages: list = self.is_file_list_packages()

            if self.utils.is_option(self.flag_no_cases, self.flags) or not self.case_sensitive:
                self.load_database()
                packages: list = self.utils.case_insensitive_pattern_matching(packages, self.data)

            if self.utils.is_option(self.flag_searches, self.flags):
                self.load_database()
                packages: list = self.choose.packages(self.data, packages, command)

            pkgs = SearchPackage(self.flags, packages, self.repository)
            pkgs.search()
            raise SystemExit()
        self.usage.help_short(1)

    def dependees(self) -> None:
        command: str = Menu.dependees.__name__

        if len(self.args) >= 2:
            self.load_database()
            self.check.is_database_empty()
            packages: list = self.is_file_list_packages()

            if self.utils.is_option(self.flag_no_cases, self.flags) or not self.case_sensitive:
                packages: list = self.utils.case_insensitive_pattern_matching(packages, self.data)

            if self.utils.is_option(self.flag_searches, self.flags):
                packages: list = self.choose.packages(self.data, packages, command)

            self.check.package_exists_in_the_database(packages, self.data)

            dependees = Dependees(self.data, packages, self.flags, self.repository)
            dependees.find()
            raise SystemExit()
        self.usage.help_short(1)

    def tracking(self) -> None:
        command: str = Menu.tracking.__name__

        if len(self.args) >= 2:
            self.load_database()
            self.check.is_database_empty()
            packages: list = self.is_file_list_packages()

            if self.utils.is_option(self.flag_no_cases, self.flags) or not self.case_sensitive:
                packages: list = self.utils.case_insensitive_pattern_matching(packages, self.data)

            if self.utils.is_option(self.flag_searches, self.flags):
                packages: list = self.choose.packages(self.data, packages, command)

            self.check.package_exists_in_the_database(packages, self.data)

            tracking = Tracking(self.data, packages, self.flags, self.repository)
            tracking.package()
            raise SystemExit()
        self.usage.help_short(1)

    def help_for_commands(self) -> None:
        """ Extra help information for commands. """
        if len(self.args) == 2:
            try:
                flags: list = self.commands[self.args[1]]
                Help(self.args[1], flags).view()
            except KeyError:
                logger = logging.getLogger(LoggingConfig.date_time)
                logger.exception(f'{self.__class__.__name__}: '
                                 f'{self.__class__.help_for_commands.__name__}')
                self.usage.help_minimal(f"{self.prog_name}: invalid argument '{''.join(self.args[1])}'")
        else:
            self.usage.help_short(1)


class SubMenu:
    """ Sub menu that separate from the main menu because of
    have no options to manage here. """

    def __init__(self, args: list):
        self.args: list = args
        self.usage = Usage()
        self.form_configs = FormConfigs()
        self.clean = Cleanings()

    def help(self) -> None:
        if len(self.args) == 1:
            self.usage.help(0)
        self.usage.help_short(1)

    def version(self) -> None:
        if len(self.args) == 1:
            version = Version()
            version.view()
            raise SystemExit()
        self.usage.help_short(1)

    def edit_configs(self) -> None:
        if len(self.args) == 1:
            self.form_configs.edit()
            raise SystemExit()
        self.usage.help_short(1)

    def clean_logs(self) -> None:
        if len(self.args) == 1:
            self.clean.logs_dependencies()
            raise SystemExit()
        self.usage.help_short(1)

    def clean_tmp(self) -> None:
        if len(self.args) == 1:
            self.clean.tmp()
            raise SystemExit()
        self.usage.help_short(1)

    def clean_data(self) -> None:
        if len(self.args) == 1:
            self.clean.db_tables()
            raise SystemExit()
        self.usage.help_short(1)


class ChoosePackages:
    """ Choose packages with dialog utility and -S, --search flag. """

    def __init__(self, repository: str):
        self.repository: str = repository

        self.utils = Utilities()
        self.dialogbox = DialogBox()

        self.is_binary: bool = self.utils.is_binary_repo(repository)

    def packages(self, data: dict, packages: list, method: str) -> list:
        height: int = 10
        width: int = 70
        list_height: int = 0
        choices: list = []
        title: str = f' Choose packages you want to {method} '

        repo_packages: list = list(data.keys())

        if method in ['remove', 'find']:
            installed: list = list(self.utils.installed_packages.values())

            for package in installed:
                package_name: str = self.utils.split_package(package)['name']
                package_version: str = self.utils.split_package(package)['version']

                for pkg in packages:
                    if pkg in package or pkg == '*':
                        choices.extend([(package_name, package_version, False, f'Package: {package}')])

        elif method == 'upgrade':
            for pkg in packages:
                for package in repo_packages:

                    if pkg == package:
                        inst_pkg: str = self.utils.is_package_installed(package)
                        inst_package_version: str = self.utils.split_package(inst_pkg)['version']
                        inst_package_build: str = self.utils.split_package(inst_pkg)['build']
                        repo_ver: str = data[package]['version']

                        if self.is_binary:
                            bin_pkg: str = data[package]['package']
                            repo_build_tag: str = self.utils.split_package(bin_pkg[:-4])['build']
                        else:
                            repo_location: str = data[package]['location']
                            repo_build_tag: str = self.utils.read_slackbuild_build_tag(
                                package, repo_location, self.repository
                            )

                        choices.extend([(package, f'{inst_package_version} -> {repo_ver}', True,
                                         f'Installed: {package}-{inst_package_version} Build: {inst_package_build} -> '
                                        f'Available: {repo_ver} Build: {repo_build_tag}')])
        else:
            for pkg in packages:
                for package in repo_packages:

                    if pkg in package or pkg == '*':
                        version: str = data[package]['version']
                        choices.extend([(package, version, False, f'Package: {package}-{version} '
                                       f'> {self.repository}')])

        if not choices:
            return packages

        text: str = f'There are {len(choices)} packages:'
        code, packages = self.dialogbox.checklist(text, packages, title, height,
                                                  width, list_height, choices)
        if code == 'cancel' or not packages:
            os.system('clear')
            raise SystemExit()

        os.system('clear')

        return packages


def main() -> None:
    args: list = sys.argv
    args.pop(0)
    usage = Usage()

    if len(args) == 0 or '' in args:
        usage.help_short(1)

    sub_menu = SubMenu(args)
    arguments_no_options: dict[str] = {
        '-h': sub_menu.help,
        '--help': sub_menu.help,
        '-v': sub_menu.version,
        '--version': sub_menu.version,
        'configs': sub_menu.edit_configs,
        '-g': sub_menu.edit_configs,
        'clean-logs': sub_menu.clean_logs,
        '-L': sub_menu.clean_logs,
        'clean-data': sub_menu.clean_data,
        '-T': sub_menu.clean_data,
        'clean-tmp': sub_menu.clean_tmp,
        '-D': sub_menu.clean_tmp
    }

    try:
        arguments_no_options[args[0]]()
    except (KeyError, IndexError):
        pass
    except KeyboardInterrupt:
        raise SystemExit(1)

    menu = Menu(args)
    arguments: dict[str] = {
        'help': menu.help_for_commands,
        'update': menu.update,
        '-u': menu.update,
        'upgrade': menu.upgrade,
        '-U': menu.upgrade,
        'check-updates': menu.check_updates,
        '-c': menu.check_updates,
        'repo-info': menu.repo_info,
        '-I': menu.repo_info,
        'build': menu.build,
        '-b': menu.build,
        'install': menu.install,
        '-i': menu.install,
        'download': menu.download,
        '-d': menu.download,
        'remove': menu.remove,
        '-R': menu.remove,
        'view': menu.view,
        '-w': menu.view,
        'find': menu.find,
        '-f': menu.find,
        'search': menu.search,
        '-s': menu.search,
        'dependees': menu.dependees,
        '-e': menu.dependees,
        'tracking': menu.tracking,
        '-t': menu.tracking
    }

    try:
        arguments[args[0]]()
    except (KeyError, IndexError):
        logger = logging.getLogger(LoggingConfig.date_time)
        logger.exception(main.__name__)
        usage.help_short(1)
    except KeyboardInterrupt:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
