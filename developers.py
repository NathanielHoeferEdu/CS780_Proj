from __future__ import print_function
"""Module containing the classes for evaluating developer comments."""

import re
import git
import logging
import argparse
import os

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
        self._repo_path = repo_path
        self._developers = []

    @property
    def repo_path(self):
        return self._repo_path

    @property
    def developers(self):
        return self._developers

    def process_devs(self):
        repo = git.Repo(path=self._repo_path)
        commits = list(repo.iter_commits())
        commits.reverse()
        progress = ProgressBar(total=len(commits))
        logger.debug("Number of commits: {}".format(len(commits)))

        curr_commit = 0
        for commit in commits:
            curr_commit += 1
            progress.progress(curr_commit, "Commits Processed")

            diff = ""
            if not commit.parents:
                diff = self._init_commit_diff(commit)
            else:
                diff_obj = commit.parents[0].diff(commit, create_patch=True)
                if diff_obj and self._is_cpp_file(diff_obj):
                    diff = unicode(diff_obj[0].diff, errors='ignore')
                else:
                    continue
            if not diff:
                continue

            name = commit.author.name
            email = commit.author.email

            logger.debug("Processing commit {}/{}: {} - diff: "
                         "{}".format(curr_commit, len(commits), commit.hexsha,
                                     diff))

            dev_index = self._find_dev(name)
            if dev_index >= 0:
                self._developers[dev_index].add_diff(diff, commit)
            else:
                developer = Developer(name, email)
                developer.add_diff(diff, commit)
                self._developers.append(developer)

    def export_dev_csv(self, filepath=None):
        filepath = filepath if filepath else DEFAULT_DEV_FILENAME
        with open(filepath, 'w') as f:
            print("{},{},{}".format("Developer", "Commit Message", "Comments"), file=f)
            for dev in self._developers:
                name = dev.name
                for diff in dev.diffs:
                    msg = diff.commit_message.replace("\n", "\\n")
                    for comment in diff.comments:
                        print("{},{},{}".format(name, msg, comment.replace("\n", "\\n")),
                              file=f)
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

    def _init_commit_diff(self, init_commit):
        """Return diff of initial commit.

        There is no easy way to collect the diff of the first commit, so this
        is the best option I found:
        https://github.com/gitpython-developers/GitPython/issues/364

        This method also requires that the '-' in the diff be replaced by '+'
        to be counted as added lines.
        """
        diff_obj = init_commit.diff(EMPTY_TREE_SHA, create_patch=True)
        diff = diff_obj[0].diff.decode("utf-8")
        diff = re.sub(re.compile("^-", re.MULTILINE), "+", diff)
        # logger.debug("Init diff: {}".format(diff))
        return diff

    def _is_cpp_file(self, diff_obj):
        """True if diff object is from a .cpp or .h file."""
        filepath = diff_obj[0].a_rawpath
        if isinstance(filepath, str):
            # print(diff_obj[0].a_rawpath)
            result = filepath.endswith((".cpp", ".h", ".cc"))
            logger.debug("Processing following file? {}, {}".format(result, filepath))
            return result
        else:
            return False

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
        logger.debug("{}, comments {}".format(self.name, diff_obj.comments))

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
    CPP_COMMENT_PATTERN = """(//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'""" \
                          """|"(?:\\.|[^\\"])*")"""

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
            else self._commit.message.strip()
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

    dev_filepath = os.path.join(args.directory, DEFAULT_DEV_FILENAME)
    print("Saving developer comments to '{}".format(dev_filepath))
    processor.export_dev_csv(dev_filepath)