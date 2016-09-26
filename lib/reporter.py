import time

import shutil

from config import LOG_FILE, LAST_LOG
from lib.runner import Module, TestCase


class Reporter(object):
    def __init__(self):
        self.modules = dict()
        self.cur_module = None
        self.start_time = time.localtime()

    def run(self, item, when='run'):
        if isinstance(item, Module) and item.name not in self.modules:
            self.modules[item.name] = list()
            self.cur_module = item.name

        try:
            getattr(item, when)()
        except AssertionError as e:
            self.modules[self.cur_module].append((item.name, 'Failed', ''))
            return 2
        except Exception as e:
            if isinstance(item, Module):
                self.modules[self.cur_module].append(('error', when, e.message or e))
            else:
                self.modules[self.cur_module].append((item.name, 'Error', e.message or e))
            return 1
        else:
            if isinstance(item, TestCase):
                self.modules[self.cur_module].append((item.name, 'Passed', ''))
            return 0

    def publish(self):
        log_file_name = time.strftime(LOG_FILE, self.start_time)
        with open(log_file_name, 'w') as f:
            for module, result in self.modules.items():
                for item, status, error in result:
                    if item == 'error':
                        f.write('{0}::Error on {1} : {2}\n'.format(module, status, error))
                    elif error:
                        f.write('{0}::{1}: {2} : {3}\n'.format(module, item, status, error))
                    else:
                        f.write('{0}::{1}: {2}\n'.format(module, item, status))

        shutil.copy(log_file_name, LAST_LOG)