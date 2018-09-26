from __future__ import absolute_import

import unittest

from developers import Diff, Developer


class TestDiff(unittest.TestCase):
    DIFF_STD = '''diff --git a/README.md b/README.md\n''' \
               '''index 1a674ef..88ec755 100644\n''' \
               '''--- a/README.md\n''' \
               '''+++ b/README.md\n''' \
               '''@@ -15,7 +15,7 @@ pip install pypeln\n''' \
               '''-With Pypeline you can easily create multi-stage\n''' \
               '''+With Pypeline you can create multi-stage data:'''

    DIFF_SINGLE = "+// Updated single Line Comment in C++\n" \
                  "+price = price * 1.05\n" \
                  "// This is single Line Comment in C++"

    DIFF_INLINE = "price = price * 1.05 // inline comment\n" \
                  "-price = price * 1.05 // updated inline comment"

    DIFF_INLINE_BLOCK = "Inline block comment /* inline block comment */\n" \
                        "-Inline block comment /* updated inline block comment */"  # nopep8

    DIFF_ONE_LINE_BLOCK = '''def quicksort():\n''' \
                          '''+/* Updated Single line block comment */\n''' \
                          '''/* Single line block comment */\n'''

    DIFF_MULTI_LINE_BLOCK = '''def quicksort():\n''' \
                            '''/* This is multi line block comment. \n''' \
                            '''in C++\n''' \
                            '''*/\n''' \
                            '''-/* Updated multi line block comment. \n''' \
                            '''-in C++\n''' \
                            '''-*/\n'''

    DIFF_BAD = '''def quicksort():\n''' \
               '''-/* Updated multi line block comment. \n''' \
               '''-in C++\n'''

    DIFF_MULTIPLE = "\n".join([DIFF_ONE_LINE_BLOCK, "",
                               DIFF_SINGLE, DIFF_INLINE])

    def test_diff_inst(self):
        diff = Diff(self.DIFF_STD)
        self.assertEqual(diff.diff, self.DIFF_STD)

    def test_diff_block(self):
        diff = Diff(self.DIFF_SINGLE)
        self.assertEqual(diff.comments,
                         ["// Updated single Line Comment in C++"])

    def test_diff_inline(self):
        diff = Diff(self.DIFF_INLINE)
        self.assertEqual(diff.comments, ["// updated inline comment"])

    def test_diff_inline_block(self):
        diff = Diff(self.DIFF_INLINE_BLOCK)
        self.assertEqual(diff.comments, ["/* updated inline block comment */"])

    def test_diff_one_line_doc(self):
        diff = Diff(self.DIFF_ONE_LINE_BLOCK)
        self.assertEqual(diff.comments,
                         ["/* Updated Single line block comment */"])

    def test_diff_multi_line_doc(self):
        diff = Diff(self.DIFF_MULTI_LINE_BLOCK)
        expected_comment = '''/* Updated multi line block comment. \n''' \
                           '''in C++\n''' \
                           '''*/'''
        self.assertEqual(diff.comments, [expected_comment])

    def test_diff_bad(self):
        diff = Diff(self.DIFF_BAD)
        self.assertEqual(diff.comments, [])

    def test_diff_multiple(self):
        diff = Diff(self.DIFF_MULTIPLE)
        expected_comment = []
        expected_comment.append('/* Updated Single line block comment */')
        expected_comment.append('// Updated single Line Comment in C++')
        expected_comment.append('// updated inline comment')
        self.assertEqual(diff.comments, expected_comment)


class TestDeveloper(unittest.TestCase):

    NAME = "Joe Bob"
    EMAIL = "JoeBob@Billy.com"

    DIFF_FIRST = '''diff --git a/README.md b/README.md\n''' \
                 '''index 1a674ef..88ec755 100644\n''' \
                 '''--- a/README.md\n''' \
                 '''+++ b/README.md\n''' \
                 '''@@ -15,7 +15,7 @@ pip install pypeln\n''' \
                 '''-With Pypeline you can easily create multi-stage\n''' \
                 '''+With Pypeline you can create multi-stage data:\n''' \
                 '''-// This is a comment\n''' \
                 '''-price = price * 1.05 // updated inline comment'''

    DIFF_SECOND = '''diff --git a/README.md b/README.md\n''' \
                  '''index 1a674ef..88ec755 100644\n''' \
                  '''--- a/README.md\n''' \
                  '''+++ b/README.md\n''' \
                  '''@@ -15,7 +15,7 @@ pip install pypeln\n''' \
                  '''-With Pypeline you can easily create multi-stage\n''' \
                  '''+With Pypeline you can create multi-stage data:\n''' \
                  '''// This is a comment\n''' \
                  '''+/* Updated Single line block comment */'''

    DIFF_THIRD = '''diff --git a/README.md b/README.md\n''' \
                 '''index 1a674ef..88ec755 100644\n''' \
                 '''--- a/README.md\n''' \
                 '''+++ b/README.md\n''' \
                 '''@@ -15,7 +15,7 @@ pip install pypeln\n''' \
                 '''-With Pypeline you can easily create multi-stage\n''' \
                 '''+With Pypeline you can create multi-stage data:\n''' \
                 '''/* This is multi line block comment. \n''' \
                 '''in C++\n''' \
                 '''*/\n''' \
                 '''-/* Updated multi line block comment. \n''' \
                 '''-in C++\n''' \
                 '''-*/'''

    DEV = Developer(name=NAME, email=EMAIL)

    def test_info(self):
        self.assertEqual(self.DEV.name, self.NAME)
        self.assertEqual(self.DEV.email, self.EMAIL)

    def test_add_initial_diff(self):
        expected_comments = ["// This is a comment",
                             "// updated inline comment"]
        self.DEV.add_diff(self.DIFF_FIRST)
        self.assertEqual(self.DEV.diff_count(), 1)
        self.assertEqual(self.DEV.comment_count(), 2)
        self.assertEqual(self.DEV.comments, expected_comments)
        self.assertEqual(self.DEV.diffs[0].diff, self.DIFF_FIRST)

    def test_add_second_diff(self):
        self.DEV.add_diff(self.DIFF_SECOND)
        self.assertEqual(self.DEV.diff_count(), 2)
        self.assertEqual(self.DEV.comment_count(), 3)

    def test_add_third_diff(self):
        self.DEV.add_diff(self.DIFF_THIRD)
        self.assertEqual(self.DEV.diff_count(), 3)
        self.assertEqual(self.DEV.comment_count(), 4)

if __name__ == '__main__':
    unittest.main()
