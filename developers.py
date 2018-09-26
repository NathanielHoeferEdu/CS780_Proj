"""Module containing the classes for evaluating developer comments."""

import re


class DevProcessing:
    pass


class Developer:
    pass


class Diff:
    """Given a standard diff, extracts modified lines and C++ comments."""

    DIFF_PATTERN = "(?:^\+|^\-)(.*$)"
    CPP_COMMENT_PATTERN = """(//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'""" \
                          """|"(?:\\.|[^\\"])*")"""

    def __init__(self, diff):
        self._diff = diff
        self._modified_lines = self._extract_mod_lines()
        self._comments = self._extract_cpp_comments()

    @property
    def diff(self):
        return self._diff

    @property
    def comments(self):
        return self._comments

    @property
    def modified_lines(self):
        return self._modified_lines

    def _extract_mod_lines(self):
        mod_lines = re.findall(self.DIFF_PATTERN, self.diff, re.MULTILINE)
        return "\n".join(mod_lines)

    def _extract_cpp_comments(self):
        comments = re.findall(self.CPP_COMMENT_PATTERN, self._modified_lines,
                              re.DOTALL | re.MULTILINE)
        return comments
