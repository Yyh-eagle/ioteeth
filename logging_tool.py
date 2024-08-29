import os
import logging
import datetime
import sys

import coloredlogs

__all__ = ["LogTool"]

class LogTool:
    def __init__(self):
        self.log_folder = 'clog' + os.sep + datetime.datetime.now().strftime('%Y%m%d')


def setup_logging(self, level=logging.DEBUG, filename=None):
    if os.path.exists(self.log_folder) is False:
        os.makedirs(self.log_folder)


    log_filename = None
    if filename is not None:
        log_filename = self.log_folder + os.sep + filename

    log_format = '%(asctime)5s - %(levelname)5s - %(lineno)4s - %(filename)18s - %(message)s'
    if log_filename is not None:
        console = logging.StreamHandler(stream=sys.stdout)
        console.setLevel(logging.getLogger().level)
        console.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(console)

    logging.basicConfig(filename=log_filename, level=level, format=log_format)
    coloredlogs.install(level=level, fmt=log_format, milliseconds=True)

def remove_log_folder(self):
    if os.path.exists(self.log_folder) is False:
        os.remove(self.log_folder)

