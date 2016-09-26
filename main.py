import argparse

from config import TEST_DIR
from lib.reporter import Reporter
from lib.runner import Collector

parser = argparse.ArgumentParser(
    usage='%(prog)s [OPTIONS] test_directory',
    description='Run tests via simple test framework',
)

if __name__ == '__main__':
    parser.add_argument('test_directory', nargs='?', default=TEST_DIR,
                        help='Directory with tests to run')
    parser.add_argument('-d', '--doc', action='store_true', dest='only_doc',
                        help='generate auto documentation (no tests will run)')

    config = parser.parse_args()
    reporter = Reporter()

    collector = Collector(config=config, reporter=reporter)
    collector.collect()

    if config.only_doc:
        collector.prepare_documentation()
    else:
        collector.run()
        reporter.publish()
