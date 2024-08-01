#!/usr/bin/env python3
"""
Mozilla Pinning script

Pin .gecko_rev.yml to the most recent suitable tag in a Mozilla repo.

Usage:
    Your current directory must be the root of comm-beta/comm-esrXX.
    The version.txt file must be up to date and match the Mozilla repo you
    are pinning to.

    $ pin_for_release.py mozilla-beta

The tags are downloaded from hg.mozilla.org in JSON format. They are
in reverse order, so the most recent tags are first. The tags are checked
against a regular expression and the first that matches is used.

Tags for a major version look something like:

    FIREFOX_82_0b2_RELEASE
    FIREFOX_82_0b2_BUILD2
    FIREFOX_82_0b2_BUILD1
    FIREFOX_82_0b1_RELEASE
    FIREFOX_82_0b1_BUILD1

Known bugs:
- Verbranches can get in the way if a chemspill necessitated a release from a
  verbranch after the next BUILD1 was tagged. So 91_10_0 gets tagged, then
  chemspill 91_9_1 gets tagged.
"""

import getpass
import json
import os
import re
import subprocess
import sys
import urllib.request

MOZ_HG_URL = "https://hg.mozilla.org/releases/{repo}"
MOZ_HG_TAG_URL = "https://hg.mozilla.org/releases/{repo}/json-tags"
# Matcher for RELEASE_BASE tags (used for late betas)
BASE_TAG_RE = r"^FIREFOX_RELEASE_{major_version}_BASE$"
# Most recent tag that's a RELEASE or BUILD1
RELEASE_TAG_RE = r"^FIREFOX_{major_version}_[\dbesr_]+(RELEASE|BUILD\d)$"

LINES = {
    "GECKO_BASE_REPOSITORY": 1,
    "GECKO_HEAD_REPOSITORY": 2,
    "GECKO_HEAD_REF": 3,
    "GECKO_HEAD_REV": 4,
}


def get_approver():
    approvers = {"rob": "rjl", "danield": "dandarnell"}
    username = getpass.getuser()
    try:
        return approvers[username]
    except KeyError:
        raise Exception(f"{username} not in approvers map! Add yourself.")


def get_json_tags(repo):
    url = MOZ_HG_TAG_URL.format(repo=repo)
    res = urllib.request.urlopen(url)
    res_body = res.read()

    j = json.loads(res_body.decode("utf-8"))
    return j


def get_last_tag(repo):
    tb_version = open("mail/config/version.txt").read()
    tb_major = tb_version.split(".")[0]
    base_tag_regex = BASE_TAG_RE.format(major_version=tb_major)
    release_tag_regex = RELEASE_TAG_RE.format(major_version=tb_major)
    base_tag_matcher = re.compile(base_tag_regex)
    release_tag_matcher = re.compile(release_tag_regex)

    def check_match(tag):
        base_m = base_tag_matcher.match(tag)
        rel_m = release_tag_matcher.match(tag)
        return base_m or rel_m

    j = get_json_tags(repo)

    for i in range(0, 10):
        tag = j["tags"][i]
        m = check_match(tag["tag"])
        if m:
            print("Found matching tag: {}".format(m.group(0)))

            print("Tag: {}".format(tag["tag"]))
            print("Rev: {}".format(tag["node"]))
            return {"tag": tag["tag"], "node": tag["node"]}

    raise Exception("No release tag found in first 10 tags downloaded.")


def get_default_rev(repo):
    j = get_json_tags(repo)
    node = j["node"]
    return {"tag": "default", "node": node}


def update_gecko_yml(repo, tagdata):
    if not os.path.isfile(".gecko_rev.yml"):
        raise Exception(
            "No .gecko_rev.yml found in current directory. Not in a comm checkout?"
        )

    with open(".gecko_rev.yml") as fp:
        data = fp.readlines()

    # Line 0 "---"
    # Line 1 GECKO_BASE_REPOSITORY
    # Line 2 GECKO_HEAD_REPOSITORY
    # Line 3 GECKO_HEAD_REF
    # Line 4 GECKO_HEAD_REV (maybe)
    def parse_line(lineno):
        line = data[lineno]
        line.strip()
        return line.split(":")

    def set_line(key, value):
        lineno = LINES[key]
        data[lineno] = "{}: {}\n".format(key, value)
        print(data[lineno].strip())

    set_line("GECKO_HEAD_REPOSITORY", MOZ_HG_URL.format(repo=repo))
    set_line("GECKO_HEAD_REF", tagdata["tag"])

    rev_line = parse_line(LINES["GECKO_HEAD_REV"])
    if len(rev_line) != 2:
        data.insert(LINES["GECKO_HEAD_REV"], "")
    set_line("GECKO_HEAD_REV", tagdata["node"])

    with open(".gecko_rev.yml", "w") as fp:
        fp.writelines(data)

    print("Success!")
    approver = get_approver()
    hg_msg = "No bug - Pin {repo} ({tag}/{shortnode}). r=release a={approver}".format(
        repo=repo, tag=tagdata["tag"], shortnode=tagdata["node"][:11], approver=approver
    )
    hg_cmd = ["hg", "commit", ".gecko_rev.yml", "-m", hg_msg]
    result = subprocess.run(hg_cmd, check=True, capture_output=True)
    print(result.stdout)
    print(result.stderr)


def update_gecko_src(repo, tagname):
    if repo.startswith("mozilla-"):
        repo = repo[8:]
    if os.path.exists("../mach"):
        hg_cmd = ["hg", "--cwd", "..", "pull", repo]
        result = subprocess.run(hg_cmd, check=True, capture_output=True)
        print(result.stdout)
        print(result.stderr)
        hg_cmd = ["hg", "--cwd", "..", "up", "-r", tagname]
        result = subprocess.run(hg_cmd, check=True, capture_output=True)
        print(result.stdout)
        print(result.stderr)
    else:
        print("Gecko src not found at '..', not updating.")


def reset_default(repo):
    tagdata = get_default_rev(repo)
    update_gecko_yml(repo, tagdata)
    


def main(repo):
    tagdata = get_last_tag(repo)
    update_gecko_yml(repo, tagdata)
    update_gecko_src(repo, tagdata["tag"])


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print(f"Usage: {__file__} mozilla-repo [--default]")
        print("    Where mozilla-repo is a valid repo, mozilla-beta or mozilla-esr*")
        sys.exit(1)
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3 and sys.argv[2] == "--default":
        reset_default(sys.argv[1])
    else:
        raise Exception("Mozilla repo name not provided.")
