#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Build a comm Docker image locally for iteration.

The in-tree ``./mach taskgraph build-image`` command only knows about images
under ``taskcluster/docker`` (gecko). It never registers the comm image paths,
so it cannot build images that live under ``comm/taskcluster/docker``. This
wrapper performs that registration and then defers to the same gecko_taskgraph
build helpers, so comm images build and tag exactly as they would in CI.

Run it through the taskgraph virtualenv (comm_taskgraph imports
mozilla_taskgraph, which is only present there):

    ./mach python --virtualenv taskgraph build-comm-image.py tb-flatpak

Use --context-only to assemble and inspect the build context without invoking
Docker (handy when debugging %include directives or recipe paths):

    ./mach python --virtualenv taskgraph build-comm-image.py tb-flatpak \\
        --context-only /tmp/ctx.tar
"""

import argparse
import os
import sys

from mozbuild.base import MozbuildObject


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "image_name",
        help="Name of the comm image to build (e.g. tb-flatpak, tb-snap).",
    )
    parser.add_argument(
        "-t",
        "--tag",
        metavar="name:tag",
        help="Tag for the built image. Defaults to '<image_name>:local'.",
    )
    parser.add_argument(
        "--context-only",
        metavar="context.tar",
        help="Only assemble the build context to this tar file; skip Docker.",
    )
    args = parser.parse_args()

    # comm_taskgraph lives under comm/taskcluster, which is not on sys.path when
    # this script is run directly via `mach python`.
    topsrcdir = MozbuildObject.from_environment().topsrcdir
    sys.path.insert(0, os.path.join(topsrcdir, "comm", "taskcluster"))

    from gecko_taskgraph.docker import build_context, build_image

    # Importing comm_taskgraph.util.docker triggers register(), which teaches
    # image_path() about the comm/taskcluster/docker image definitions. This must
    # happen before build_image()/build_context() resolve the image path below.
    import comm_taskgraph.util.docker  # noqa: F401

    if args.context_only:
        build_context(args.image_name, args.context_only, os.environ)
        print(f"Wrote context for {args.image_name} to {args.context_only}")
    else:
        tag = args.tag or f"{args.image_name}:local"
        build_image(args.image_name, tag, os.environ)

    return 0


if __name__ == "__main__":
    sys.exit(main())
