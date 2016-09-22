from os import path

_WORK_DIR = path.dirname(__file__)
TEST_DIR = path.join(_WORK_DIR, 'tests')
LOG_FILE = path.join(_WORK_DIR, '%Y-%m-%d-%H-%M-%S.log')
DOC_FILE = path.join(_WORK_DIR, 'tests_doc', 'doc.txt')