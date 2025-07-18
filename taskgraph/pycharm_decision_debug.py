#!python3

import os
import sys
import subprocess
import time

from build import mach_bootstrap
from mozversioncontrol import (
    get_repository_object,
    InvalidRepoPath,
)


def ancestors(path):
    while path:
        yield path
        path, child = os.path.split(path)
        if child == '':
            break


def find_topsrcdir():
    for path in ancestors(os.getcwd()):
        try:
            get_repository_object(path)
        except InvalidRepoPath:
            continue
        # Identify GECKO_SRC vs COMM_SRC by the presence of a file named "mach"
        if os.path.exists(os.path.join(path, 'mach')):
            return path
        else:
            continue

    raise Exception('Unable to find topsrcdir at {}'.format(os.getcwd()))


def get_hg_changeset(root):
    return subprocess.check_output("hg -R %s parent --template='{node}'" % root, shell=True)
    # return '4eac5c4c23a31f05af4f150d51a47e474cf99925' if 'comm' in root else
    # '9b4c8fb46d850db196b0ed6aad0a35b85b178745'


def get_buildid():
    return int(time.time())


def load_mach(dir_path, mach_path):
    import imp
    with open(mach_path, 'r') as fh:
        imp.load_module('mach_bootstrap', fh, mach_path,
                        ('.py', 'r', imp.PY_SOURCE))
    import mach_bootstrap
    return mach_bootstrap.bootstrap(dir_path)


topsrcdir = find_topsrcdir()
gecko_rev = get_hg_changeset(topsrcdir)
comm_rev = get_hg_changeset(os.path.join(topsrcdir, 'comm'))

substs = dict([
    ('GECKO_BASE_REPOSITORY', "https://hg-edge.mozilla.org/mozilla-unified"),
    ('GECKO_HEAD_REPOSITORY', "https://hg-edge.mozilla.org/mozilla-central"),
    ('MOZ_SOURCE_CHANGESET', gecko_rev),
    ('GECKO_HEAD_REF', gecko_rev),
    ('GECKO_HEAD_REV', gecko_rev),
    ('COMM_BASE_REPOSITORY', "https://hg-edge.mozilla.org/comm-central"),
    ('COMM_HEAD_REPOSITORY', "https://hg-edge.mozilla.org/comm-central"),
    ('COMM_HEAD_REF', comm_rev),
    ('COMM_HEAD_REV', comm_rev),

    ('MOZ_BUILD_DATE', get_buildid()),
    ('MOZ_AUTOMATION', 1),
    ('MOZ_INCLUDE_SOURCE_INFO', 1),
    ('PUSH_DATE', get_buildid(),)])

args = []

for a in sys.argv[1:]:
    args.append(a.format(**substs))
print(args)

# time.sleep(90)

mach = mach_bootstrap.bootstrap(os.path.abspath(topsrcdir))
mach.run(args)
