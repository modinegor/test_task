import os
import tempfile
from os import path
from subprocess import call
from stat import *
from pwd import getpwuid
from grp import getgrgid

import shutil

from config import NFS_SERVER, NFS_DIR
from lib.runner import parametrize

name = 'Owner'
description = 'Verify operations on changing owners'


def setup(context):
    context.dirpath = dirpath = tempfile.mkdtemp()
    context.test_file = test_file = path.join(dirpath, 'test_file')
    context.test_directory = test_dir = path.join(dirpath, 'test_dir')

    call(['touch', path.join(NFS_DIR, path.basename(test_file))])
    call(['mkdir', path.join(NFS_DIR, path.basename(test_dir))])

    call(['mount', '-t', 'nfs4', NFS_SERVER + ':' + NFS_DIR, dirpath])


def teardown(context):
    if context.dirpath:
        call(['umount', context.dirpath])
        shutil.rmtree(context.dirpath)

    shutil.rmtree(path.join(NFS_DIR, path.basename(context.test_directory)))
    os.remove(path.join(NFS_DIR, path.basename(context.test_file)))


def get_file_ownership(filename):
    return getpwuid(os.stat(filename).st_uid).pw_name, getgrgid(os.stat(filename).st_gid).gr_name


@parametrize('item', ['directory', 'file'])
def test_case_change_owner_user(context, item):
    """Change user owner for a {item}

    Steps:
    1. Change user owner for a {item}
    2. Change it back

    Expected results:
    1. Owner was changed to another user and then back
    """
    item = getattr(context, 'test_' + item)
    init_user = get_file_ownership(item)[0]
    new_owner = ({'egor', 'root'} - {init_user}).pop()
    call(['chown', new_owner, item])

    assert get_file_ownership(item)[0] == new_owner

    call(['chown', init_user, item])

    assert get_file_ownership(item)[0] == init_user


@parametrize('item', ['directory', 'file'])
def test_case_change_owner_group(context, item):
    """Change group owner for a {item}

    Steps:
    1. Change group owner for a {item}
    2. Change it back

    Expected results:
    1. Owner was changed to another user and then back
    """
    item = getattr(context, 'test_' + item)
    init_group = get_file_ownership(item)[1]
    new_group = ({'egor', 'root'} - {init_group}).pop()
    call(['chgrp', new_group, item])

    assert get_file_ownership(item)[1] == new_group

    call(['chgrp', init_group, item])

    assert get_file_ownership(item)[1] == init_group
