import tempfile
from os import chdir, path, getcwd

from subprocess import call, Popen

import shutil

from config import NFS_SERVER, NFS_DIR
from lib.runner import parametrize


name = 'Content'
description = 'Check operations on content'


def setup(context):
    context.dirpath = dirpath = tempfile.mkdtemp()
    context.workdir = getcwd()
    call(['mount', '-t', 'nfs4', NFS_SERVER + ':' + NFS_DIR, dirpath])
    chdir(dirpath)


def teardown(context):
    chdir(context.workdir)
    if context.dirpath:
        call(['umount', context.dirpath])
        shutil.rmtree(context.dirpath)


@parametrize('file_name', ['simple', 'a' * 255, 'a', '!@#$%^&*()_+'])
def test_case_create_file_root_dir(context, file_name):
    """Create and delete file with name {file_name}

    Steps:
    1. Create file '{file_name}'
    2. Delete it file

    Expected results:
    1. File created
    2. File deleted
    """
    call(['touch', file_name])
    assert path.isfile(path.join(context.dirpath, file_name))

    call(['rm', '-f', file_name])
    assert not path.isfile(path.join(context.dirpath, file_name))


@parametrize('dir_name', ['simple', 'a' * 255, 'a', '!@#$%^&*()_+'])
def test_case_create_dir_root_dir(context, dir_name):
    """Create and delete directory with name {dir_name}

    Steps:
    1. Create directory '{dir_name}'
    2. Delete it directory

    Expected results:
    1. Directory is created
    2. Directory is deleted
    """
    call(['mkdir', dir_name])
    assert path.isdir(path.join(context.dirpath, dir_name))

    call(['rm', '-fr', dir_name])
    assert not path.isdir(path.join(context.dirpath, dir_name))