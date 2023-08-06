#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
from multiprocessing import Process

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.views.asciibox import AsciiBox
from slpkg.progress_bar import ProgressBar


class MultiProcess(Configs):

    def __init__(self, flags: list):
        super(Configs, self).__init__()

        self.utils = Utilities()
        self.progress = ProgressBar()
        self.ascii = AsciiBox()

        self.stderr = None
        self.stdout = None

        self.option_for_no_silent: bool = self.utils.is_option(
            ('-n', '--no-silent'), flags)

    def process(self, command: str, filename: str, progress_message: str) -> None:
        """ Starting multiprocessing install/upgrade process. """
        if self.silent_mode and not self.option_for_no_silent:
            done: str = f'{self.yellow}{self.ascii.done}{self.endc}'
            failed: str = f'{self.red}{self.ascii.failed}{self.endc}'
            self.stderr = subprocess.DEVNULL
            self.stdout = subprocess.DEVNULL

            # Starting multiprocessing
            process_1 = Process(target=self.utils.process, args=(command, self.stderr, self.stdout))
            process_2 = Process(target=self.progress.progress_bar, args=(progress_message, filename))

            process_1.start()
            process_2.start()

            # Wait until process 1 finish
            process_1.join()

            # Terminate process 2 if process 1 finished
            if not process_1.is_alive():
                process_2.terminate()
                if process_1.exitcode != 0:
                    print(f"\r{'':>2}{self.bred}{self.ascii.bullet}{self.endc} {filename} {failed}{' ' * 17}", end='\r')
                else:
                    print(f"\r{'':>2}{self.bgreen}{self.ascii.bullet}{self.endc} {filename} {done}{' ' * 17}", end='\r')

            # Restore the terminal cursor
            print('\x1b[?25h', self.endc)
        else:
            self.utils.process(command, self.stderr, self.stdout)
