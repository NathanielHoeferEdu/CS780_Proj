from __future__ import print_function
"""Module containing the classes for evaluating developer comments."""

import re
import git
import logging
import argparse
import os
import csv

from dev_utils import ProgressBar

logger = logging.getLogger('dev')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler(filename='dev_tool.log', mode='w')
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
DEFAULT_DEV_FILENAME = "dev_comments.csv"
DEFAULT_STATS_FILENAME = "repo_stats.csv"


class DevProcessor:

    def __init__(self, repo_path):
        self._repo = git.Repo(path=repo_path)
        self._repo_path = repo_path
        self._repo_name = os.path.basename(self._repo.working_dir)
        self._developers = []

    @property
    def repo_path(self):
        return self._repo_path

    @property
    def developers(self):
        return self._developers

    def process_devs(self):
        commits = list(self._repo.iter_commits())
        commits.reverse()
        progress = ProgressBar(total=len(commits))
        logger.debug("Number of commits: {}".format(len(commits)))

        curr_commit = 0
        for commit in commits:
            curr_commit += 1
            progress.progress(curr_commit, "Commits Processed")

            diffs = self._extract_diffs(commit)
            if not diffs:
                continue

            name = commit.author.name.encode('utf-8')
            email = commit.author.email.encode('utf-8')

            log_intro = "Processing commit {}/{} " \
                        "{}:".format(curr_commit, len(commits),commit.hexsha)
            commit_msg = commit.message.encode('utf-8').strip()
            log_commit_msg = "{}".format(commit_msg)
            process_commit_log = "\n".join([log_intro, log_commit_msg, "="*len(commit_msg)])
            logger.debug(process_commit_log)

            dev_index = self._find_dev(name)
            if dev_index >= 0:
                developer = self._developers[dev_index]
            else:
                self._developers.append(Developer(name, email))
                developer = self._developers[-1]

            for diff in diffs:
                logger.debug("Processing diff {}".format(diff))
                developer.add_diff(diff, commit)


    def export_dev_csv(self, filepath=None):
        if not filepath:
            filepath = "".join([self._repo_name, "_comments.csv"])
        print("\nSaving developer comments to '{}".format(filepath))

        with open(filepath, 'w') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["Repository", self._repo_path])
            writer.writerow([])
            writer.writerow(["Developer", "Commit Message", "Comments"])
            for dev in self._developers:
                name = dev.name
                for diff in dev.diffs:
                    msg, _, _ = diff.commit_message.partition("\n")
                    for comment in diff.comments:
                        writer.writerow([name, msg, comment.replace("\n", "\\n")])
                        name = ""
                        msg = ""


    def _pairwise(self, iterable):
        it = iter(iterable)
        a = next(it, None)
        for b in it:
            yield (a, b)
            a = b

    def _find_dev(self, name):
        """Return the index of developer by name."""
        for i in range(len(self._developers)):
            if self._developers[i].name == name:
                return i
        return -1

    def _extract_diffs(self, commit):
        """If diffs exists, return list(str) of diffs."""
        diffs = []
        if not commit.parents:
            return self._init_commit_diffs(commit)

        if not self._is_merge(commit):
            parent = commit.parents[0]
            diff_obj = parent.diff(commit, create_patch=True)
            if diff_obj:
                for diff in diff_obj:
                    if self._is_cpp_file(diff):
                        diffs.append(unicode(diff.diff, errors='ignore'))
        return diffs

    def _init_commit_diffs(self, init_commit):
        """Return diffs of initial commit.

        There is no easy way to collect the diff of the first commit, so this
        is the best option I found:
        https://github.com/gitpython-developers/GitPython/issues/364

        This method also requires that the '-' in the diff be replaced by '+'
        to be counted as added lines.
        """
        diff_obj = init_commit.diff(EMPTY_TREE_SHA, create_patch=True)
        diffs = []
        for diff in diff_obj:
            if self._is_cpp_file(diff):
                diff_str = diff.diff.decode("utf-8")
                diff_str = re.sub(re.compile("^-", re.MULTILINE), "+", diff_str)
                if diff_str:
                    diffs.append(diff_str)
        return diffs

    def _is_cpp_file(self, diff):
        """True if diff object is from a C++ file."""
        filepath = diff.b_rawpath if diff.b_rawpath else diff.a_rawpath
        if isinstance(filepath, str):
            result = filepath.endswith((".cpp", ".h", ".cc"))
            logger.debug("Processing following file? {}, {}".format(result, filepath))
            return result
        else:
            logger.debug("Not processing file: {}".format(filepath))
            return False

    def _is_merge(self, commit):
        """True if commit object is a result of a merge."""
        return len(commit.parents) > 1

class Developer:
    """Tracks number of diffs and comments of a particular developer."""

    def __init__(self, name, email):
        """Developer Init.
        :param str name: name of developer
        :param str email: email of developer
        """
        self._name = name
        self._email = email
        self._diffs = []
        self._comment_count = 0

    @property
    def name(self):
        """Name of developer.
        :returns: str
        """
        return self._name

    @property
    def email(self):
        """Email of developer.
        :returns: str
        """
        return self._email

    @property
    def diffs(self):
        """List of all the currently added diffs.
        :returns: list(Diff)
        """
        return self._diffs

    @property
    def comments(self):
        """List of all the comments found within the diffs.
        :returns: list(str)
        """
        all_comments = []
        for diff in self._diffs:
            all_comments.extend(diff.comments)
        return all_comments

    def add_diff(self, diff, commit=None):
        """Associate a diff to this developer.
        :param str diff: string represntation of diff.
        :param str commit_sha: Commit identifier, usually SHA-1 checksum
        """
        diff_obj = Diff(diff, commit)
        self._comment_count += len(diff_obj.comments)
        self._diffs.append(diff_obj)
        logger.debug("{}, added comments {}".format(self.name, diff_obj.comments))

    def diff_count(self):
        """Number of diffs currently associated with the developer.
        :returns: int
        """
        return len(self._diffs)

    def comment_count(self):
        """Number of comments currently associated with the developer.
        :returns: int
        """
        return self._comment_count


class Diff:
    """Given a standard diff, extracts added lines and C++ comments."""

    DIFF_PATTERN = "^\+(.*$)"
    CPP_COMMENT_PATTERN = """(?: |^)(//.*?$|/\*.*?\*/)"""

    def __init__(self, diff, commit=None):
        """Diff Init.
        :param str diff: String representation of diff
        :param str commit_sha: Commit identifier, usually SHA-1 checksum
        """
        self._diff = diff
        self._commit = commit
        self._modified_lines = self._extract_mod_lines()
        self._comments = self._extract_cpp_comments()

    @property
    def diff(self):
        """Return string representation of diff."""
        return self._diff

    @property
    def commit_message(self):
        message = "No commit message" if not self._commit \
            else self._commit.message.encode('utf-8').strip()
        return message

    @property
    def comments(self):
        """Return list of comments found within the modified lines of diff."""
        return self._comments

    @property
    def modified_lines(self):
        """Lines of code as str within diff beginning with '-' or '+'."""
        return self._modified_lines

    def _extract_mod_lines(self):
        mod_lines = re.findall(self.DIFF_PATTERN, self._diff, re.MULTILINE)
        return "\n".join(mod_lines)

    def _extract_cpp_comments(self):
        comments = re.findall(self.CPP_COMMENT_PATTERN, self._modified_lines,
                              re.DOTALL | re.MULTILINE)
        return comments


script_desc = "Extracts comments from developers generated over the " \
              "lifetime of a repository."

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=script_desc)
    parser.add_argument("repository", type=str, default=None,
                        help="Path of the repository to extract comments.")
    parser.add_argument("-d", "--directory", type=str, default=".",
                        help="Directory of where to store the csv files.")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print("{} is not a directory".format(args.directory))
        exit(1)

    processor = DevProcessor(args.repository)
    processor.process_devs()

    os.chdir(args.directory)
    processor.export_dev_csv()