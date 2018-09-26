from __future__ import absolute_import

import unittest

from developers import Diff


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


if __name__ == '__main__':
    unittest.main()
