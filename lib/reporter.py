import time

from config import LOG_FILE
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
                self.modules[self.cur_module].append(('error', when, e.message))
            else:
                self.modules[self.cur_module].append((item.name, 'Error', e.message))
            return 1
        else:
            if isinstance(item, TestCase):
                self.modules[self.cur_module].append((item.name, 'Passed', ''))
            return 0

    def publish(self):
        with open(time.strftime(LOG_FILE, self.start_time), 'w') as f:
            for module, result in self.modules.items():
                for item, status, error in result:
                    if item == 'error':
                        f.write('{0}::Error on {1} : {2}\n'.format(module, status, error))
                    elif error:
                        f.write('{0}::{1}: {2} : {3}\n'.format(module, item, status, error))
                    else:
                        f.write('{0}::{1}: {2}\n'.format(module, item, status))