from os import listdir, path
import re
import sys

from config import DOC_FILE


class Collector(object):
    def __init__(self, config, reporter):
        self.config = config
        self.reporter = reporter
        self.items = list()

    def collect(self):
        test_dir = self.config.test_directory
        for fl in listdir(test_dir):
            if re.match('test_suite_.*\.py$', fl):
                self.items.append(Module(path.join(test_dir, fl), reporter=self.reporter))

    def run(self):
        for item in self.items:
            if not self.reporter.run(item=item, when='setup'):
                self.reporter.run(item=item, when='run')
                self.reporter.run(item=item, when='teardown')

    def prepare_documentation(self):
        new_line = True
        with open(DOC_FILE, 'w') as df:
            for module in self.items:
                if not new_line:
                    df.write('-' * 40 + '\n')
                df.write('Test Suite : {0}\n'.format(module.name))
                if module.description:
                    df.write('Description: {0}\n'.format(module.description))
                new_line = False
                df.write('\n')

                for case in module.items:
                    df.write('Test Case: {0}\n'.format(case.name))
                    case_doc = case.func_obj.__doc__
                    if case.arg_names:
                        case_doc = case_doc.format(**dict(zip(case.arg_names, case.arg_values)))
                    df.write('\n'.join([line.strip() for line in case_doc.split('\n') if line]))
                    df.write('\n')


class Context(object):
    def __init__(self):
        self._dict = dict()

    def __setattr__(self, key, value):
        if key[0] == '_':
            self.__dict__[key] = value
        else:
            self._dict[key] = value

    def __getattr__(self, item):
        if item in self._dict:
            return self._dict[item]
        return self.__dict__[item]


class Module(object):
    def __init__(self, fpath, reporter):
        self.fpath = fpath
        self.reporter = reporter
        self._obj = None
        self.items = list()
        self.context = Context()

        self.name = getattr(self.obj, 'name', self.obj.__name__.replace('test_suite_', ''))
        self.description = getattr(self.obj, 'description', '')

        self.collect()

    @property
    def obj(self):
        if not self._obj:
            self._obj = self._getobj()
            self._obj.__dict__['context'] = dict()
        return self._obj

    def _getobj(self):
        self._ensuresyspath()
        modname = re.match('(.+)\.py', path.basename(self.fpath)).groups()[0]
        __import__(modname)
        return sys.modules[modname]

    def _ensuresyspath(self):
        test_dir = path.dirname(self.fpath)
        if test_dir not in sys.path:
            sys.path.append(test_dir)

    def setup(self):
        setup_func = getattr(self.obj, 'setup', None)
        if setup_func:
            setup_func(context=self.context)

    def teardown(self):
        teardown_func = getattr(self.obj, 'teardown', None)
        if teardown_func:
            teardown_func(context=self.context)

    def collect(self):
        for name, obj in getattr(self.obj, '__dict__', dict()).items():
            if name.startswith('test_case_') and hasattr(obj, '__call__'):
                self.items.extend(self._genitems(obj))

    def _genitems(self, funcobj):
        items = list()
        if hasattr(funcobj, 'parametrize'):
            argnames, argvalues = getattr(funcobj, 'parametrize')
            argnames = argnames.split(',')

            for argval in argvalues:
                items.append(TestCase(context=self.context,
                                      func_obj=funcobj,
                                      arg_names=argnames,
                                      arg_values=argval if isinstance(argval, dict) or isinstance(argval, tuple) else [argval]))

        else:
            items.append(TestCase(context=self.context,
                                  func_obj=funcobj))
        return items

    def run(self):
        for item in self.items:
            self.reporter.run(item=item)


class TestCase(object):
    def __init__(self, context, func_obj, arg_names=None, arg_values=None):
        self.context = context
        self.func_obj = func_obj
        self.arg_names = arg_names or ()
        self.arg_values = arg_values or ()

        self.name = func_obj.__name__.replace('test_case_', '')
        if arg_names:
            self.name = '{0}[{1}]'.format(self.name,
                                          ','.join(['{0}={1}'.format(name, '`{0}`*{1}'
                                                                     .format(value[0], len(value)) if value and
                                                                                                      isinstance(value, str) and len(value) > 50 and
                                                                                                      value == value[0] * len(value) else value)
                                                    for name, value in zip(arg_names, arg_values)]))

    def run(self):
        args_dict = dict(context=self.context)
        args_dict.update(dict(zip(self.arg_names, self.arg_values)))
        self.func_obj(**args_dict)


class Parametrize(object):
    def __init__(self, *args):
        self.args = args

    def __call__(self, func):
        setattr(func, 'parametrize', self.args)
        return func


parametrize = Parametrize
