<h2 align="center"><u>Thunderbird Releng Scripts</u></h2>

<h4 align="center"> All your uplift are belong to us. </h4>

<p align="center">
<br>
</p>

### [+] Description
This repository contains scripts that are used for Thunderbird development and release driving.

### [+] Scripts in this repository

* pull-comm
  * Works with a unified repository to pull mozilla- and matching comm- trees
  * Assumes firefoxtree extension is installed

  * Set up a repository checkout
    * hg clone `mozilla-central` and `comm-central` as usual.
  * To update both repositories to their latest tips:
    * `cd comm`
    * `pull-comm comm`
    * Both repositories must be in a clean state
  * Also works with `comm-beta` and `comm-esr102`

* tc-signin
  * Log into Taskcluster in a web browser. The returned auth token is saved
    to Taskcluster's config file to keep you logged in.

* rerun-failed-tasks
  * Have a bunch of failed tasks on a push? `rerun-fauled-tasks` can rerun
   those fakled jobs. 
  * $ rerun-failed-tasks DECISION_TASK_ID
  * Optionally, pass a string to match against the job names to run a subset
    of those failures
  * $ rerun-failed-tasks DECISION_TASK_ID shippable-l10n
    * Reruns only failed l10n jobs on try-c-c.

#### Relesse scripts

* update_version.sh <new version>
  * Update mail/config/version.txt and version_display.txt with the new
  version before it gets too dark and you can't find your glasses.
* pin_for_release.py  <mozilla-repo>
  * Updates .gecko_rev.yml to the latest BUILD or RELEASE tag in the given
    mozilla repo.
  * ex: pin_for_release.py mozilla-esr102
  * Remember to check that the right tag and revision was selected.
* graft_uplift.sh <approver> <hg rev>
  * To effectively use graft_uplift.sh, you need a local repository with
    comm-central, comm-beta, and comm-esr102 all pulled in.
  * ex: graft_uplift.sh wsmwk 374218d443ff
* import_urlpatch.sh <approver> <url>
  * For uplifting patches from a URL, such as a Bugzilla attachment
  * ex: import_urlpatch.sh wsmwk 'https://bug1778867.bmoattachments.org/attachment.cgi?id=9285695'

