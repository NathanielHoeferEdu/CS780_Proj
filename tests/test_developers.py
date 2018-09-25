import unittest

from developers import *

class TestDiff(unittest.TestCase):

    def test_diff_inst(self):
        diff_str = repo.git.diff(commits[5], commits[6])

