import os
import tempfile
from os import path
from subprocess import call
from stat import *

import shutil

from config import NFS_SERVER, NFS_DIR
from lib.runner import parametrize

name = 'Permissions'
description = 'Verify operations on permissions'


def setup(context):
    context.dirpath = dirpath = tempfile.mkdtemp()
    context.test_file = test_file = path.join(dirpath, 'test_file')
    context.test_dir = test_dir = path.join(dirpath, 'test_dir')

    call(['touch', path.join(NFS_DIR, path.basename(test_file))])
    call(['mkdir', path.join(NFS_DIR, path.basename(test_dir))])

    call(['mount', '-t', 'nfs4', NFS_SERVER + ':' + NFS_DIR, dirpath])


def teardown(context):
    if context.dirpath:
        call(['umount', context.dirpath])
        shutil.rmtree(context.dirpath)

    shutil.rmtree(path.join(NFS_DIR, path.basename(context.test_dir)))
    os.remove(path.join(NFS_DIR, path.basename(context.test_file)))


@parametrize('mask', [777, 666, 444])
def test_case_change_file_permissions(context, mask):
    """Change permissions for a file to "{mask}"

    Steps:
    1. Change file mask to value {mask}

    Expected results:
    1. Mask of file has been successfully changed

    """
    call(['chmod', str(mask), context.test_file])
    assert oct(os.stat(context.test_file)[ST_MODE]).endswith(str(mask))


@parametrize('mask', [777, 666, 444])
def test_case_change_dir_permissions(context, mask):
    """Change permissions for a directory to "{mask}"

    Steps:
    1. Change directory mask to value {mask}

    Expected results:
    1. Mask of directory has been successfully changed

    """
    call(['chmod', str(mask), context.test_dir])
    assert oct(os.stat(context.test_dir)[ST_MODE]).endswith(str(mask))