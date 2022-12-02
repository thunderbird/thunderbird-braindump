#!/usr/bin/python3

# Takes a Taskcluster task definition that you can download from the
# taskcluster web UI, and does enough of the setup so you can run
# the meat of the task in a local docker.
# Example:
#  Toolchain build - does the M-C checkout and then any tool/artifact
#     downloads.
# At least that's the idea...
#
# TODO: better error checking!

import sys
import os
import json



def run_task(payload):
    """
    Extracts the environment and command from a task description and
    runs it.
    """
    env = payload["env"]
    command = payload["command"]

    env["TASKCLUSTER_ROOT_URL"] = 'https://firefox-ci-tc.services.mozilla.com'

    run_environ = dict(os.environ)
    run_environ.update(env)

    with open('mkenv.py', 'w') as fp:
        fp.write("""#!/usr/bin/python3

import json
import os

env = json.loads(open('env.json', 'r').read())
run_env = dict(os.environ)
run_env.update(env)

os.execve('/bin/bash', ['/bin/bash', '--login'], run_env)
""")

    with open('env.json', 'w') as fp:
        j = json.dumps(env)
        fp.write(j)

    os.chmod('mkenv.py', 0o755)

    os.execve(command[0], command, run_environ)


def main():
    data = sys.stdin.read()

    if not data:
        print("No data read?")
        sys.exit(2)

    payload = json.loads(data)["payload"]
    del data

    run_task(payload)
    

if __name__ == '__main__':
    main()
