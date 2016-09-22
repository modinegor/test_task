from os import listdir
import re

import sys

from config import *


def run():
    collector = Collector()
    collector.collect()


class Collector(object):
    def __init__(self):
        self.items = list()

    def collect(self):
        for fl in listdir(TEST_DIR):
            if re.match('test_suite_*.py', fl):
                self.items.append(Module(path.join(TEST_DIR, fl)))

    def run(self):
        for item in self.items:
            self.run_test_protocol(item)

    def run_test_protocol(self, item):
        self.run_and_report(item, 'setup')
        self.run_and_report(item, 'run')
        self.run_and_report(item, 'teardown')

    def run_and_report(self, item, when):
        try:
            getattr(item, when)()
        except Exception:
            pass


class Module(object):
    def __init__(self, fpath):
        self.fpath = fpath
        self._obj = None
        self.items = list()
        self.collect()

    @property
    def obj(self):
        if not self._obj:
            self._obj = self._getobj()
        return self._obj

    def _getobj(self):
        self._ensuresyspath()
        modname = re.match('(.+)\.py', path.basename()).groups()[0]
        __import__(modname)
        return sys.modules[modname]

    def _ensuresyspath(self):
        test_dir = path.dirname(self.fpath)
        if test_dir not in sys.path:
            sys.path.append(test_dir)

    def setup(self):
        setup_func = getattr(self.obj, 'setup')
        if setup_func:
            setup_func()

    def teardown(self):
        teardown_func = getattr(self.obj, 'teardown')
        if teardown_func:
            teardown_func()

    def collect(self):
        for item in getattr(self.obj, '__dict__', dict()):
            self.items.extend(self._genitems(item))

    def _genitems(self, funcobj):
        if hasattr(funcobj, 'parametrize'):
            items = list()
            argnames, argvalues = getattr(funcobj, 'parametrize')
            argnames = argnames.split(',')

            for argval in argvalues:
                items.append(TestCase(func_obj=funcobj,
                                      arg_names=argnames,
                                      arg_values=[argval] if isinstance(argval, basestring) else argval))

            return items
        return TestCase(funcobj)

    def run(self):
        for item in self.items:
            item.run()


class TestCase(object):
    def __init__(self, func_obj, arg_names=None, arg_values=None):
        self.func_obj = func_obj
        self.arg_names = arg_names or ()
        self.arg_values = arg_values or ()

    def run(self):
        self.func_obj(**dict(zip(self.arg_names, self.arg_values)))


class Parametrize(object):
    def __init__(self, args=None):
        self.args = args or ()

    def __call__(self, *args):
        func = args[0]
        if len(args) == 1 and self.istestfunc(func):
            setattr(func, 'parametrize', args)
        return self.__class__(args=args)

    def istestfunc(self, func):
        return hasattr(func, '__call__')


parametrize = Parametrize
