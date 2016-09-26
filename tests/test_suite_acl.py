import getpass
import os
import random
import string
import tempfile
from subprocess import call, Popen, PIPE

import shutil

from os import path

from config import NFS_SERVER, NFS_DIR

name = 'ACL'
description = 'Check ACL'


def setup(context):
    context.user = user = getpass.getuser()
    context.dirpath = dirpath = tempfile.mkdtemp()

    context.test_file = test_file = path.join(dirpath, 'test_file')
    nfs_file = path.join(NFS_DIR, path.basename(test_file))
    call(['touch', nfs_file])

    context.file_content = 'test'
    with open(nfs_file, 'w') as fl:
        fl.write(context.file_content)

    call(['mount', '-t', 'nfs4', NFS_SERVER + ':' + NFS_DIR, dirpath])
    call(['nfs4_setfacl', '-s', 'A::EVERYONE@:r', test_file])


def teardown(context):
    if context.dirpath:
        call(['umount', context.dirpath])
        shutil.rmtree(context.dirpath)

    os.remove(path.join(NFS_DIR, path.basename(context.test_file)))


def test_case_check_read(context):
    """Check read operation on allowed file by ACL

    """
    pipe = Popen(['cat', context.test_file], stdout=PIPE)
    assert pipe.communicate()[0] == context.file_content


def test_case_check_write(context):
    """Check write operation on not allowed file by ACL

    """
    os.system('echo "{0}" > {1}'.format(''.join(random.choice(string.ascii_lowercase) for i in xrange(10)), context.test_file))
    with open(context.test_file) as fl:
        assert fl.read() == context.file_content