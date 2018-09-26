"""Module containing the classes for evaluating developer comments."""

import re


class DevProcessing:
    pass


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

    def add_diff(self, diff):
        """Associate a diff to this developer.
        :param str diff: string represntation of diff.
        """
        diff_obj = Diff(diff)
        self._comment_count += len(diff_obj.comments)
        self._diffs.append(diff_obj)

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
    """Given a standard diff, extracts modified lines and C++ comments."""

    DIFF_PATTERN = "(?:^\+|^\-)(.*$)"
    CPP_COMMENT_PATTERN = """(//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'""" \
                          """|"(?:\\.|[^\\"])*")"""

    def __init__(self, diff):
        """Diff Init.
        :param str diff: String representation of diff
        """
        self._diff = diff
        self._modified_lines = self._extract_mod_lines()
        self._comments = self._extract_cpp_comments()

    @property
    def diff(self):
        """Return string representation of diff."""
        return self._diff

    @property
    def comments(self):
        """Return list of comments found within the modified lines of diff."""
        return self._comments

    @property
    def modified_lines(self):
        """Lines of code as str within diff beginning with '-' or '+'."""
        return self._modified_lines

    def _extract_mod_lines(self):
        mod_lines = re.findall(self.DIFF_PATTERN, self.diff, re.MULTILINE)
        return "\n".join(mod_lines)

    def _extract_cpp_comments(self):
        comments = re.findall(self.CPP_COMMENT_PATTERN, self._modified_lines,
                              re.DOTALL | re.MULTILINE)
        return comments
