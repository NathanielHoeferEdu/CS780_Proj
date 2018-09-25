from __future__ import absolute_import

import unittest

from developers import Diff

class TestDiff(unittest.TestCase):
    DIFF_STD = '''diff --git a/README.md b/README.md\n''' \
               '''index 1a674ef..88ec755 100644\n''' \
               '''--- a/README.md\n''' \
               '''+++ b/README.md\n''' \
               '''@@ -15,7 +15,7 @@ pip install pypeln\n''' \
               '''-With Pypeline you can easily create multi-stage data pipelines using 3 type of workers:\n''' \
               '''+With Pypeline you can create multi-stage data pipelines using with 3 type of workers:'''

    DIFF_BLOCK = "# increase price to 5%\n" \
                 "price = price * 1.05"

    DIFF_INLINE = "price = price * 1.05  # increase price to 5%"

    DIFF_ONE_LINE_DOC = '''def quicksort():\n''' \
                        '''""" sort the list using quicksort algorithm """'''

    DIFF_MULTI_LINE_DOC = '''def quicksort():\n''' \
                        '''""" sort the list using quicksort algorithm \n''' \
                        '''Second Line\n''' \
                        '''First Line\n''' \
                        '''\n''' \
                        '''"""'''

    DIFF_BAD = '''def quicksort():\n''' \
                '''""" sort the list using quicksort algorithm \n''' \
                '''Second Line"""\n''' \
                '''First Line\n''' \
                '''\n''' \
                '''"""'''

    DIFF_MULTIPLE = "\n".join([DIFF_ONE_LINE_DOC, "", DIFF_BLOCK, DIFF_INLINE])

    def test_diff_inst(self):
        diff = Diff(self.DIFF_STD)
        self.assertEqual(diff.diff, self.DIFF_STD)

    def test_diff_block(self):
        diff = Diff(self.DIFF_BLOCK)
        self.assertEqual(diff.comments(), ["# increase price to 5%"])

    def test_diff_inline(self):
        diff = Diff(self.DIFF_INLINE)
        self.assertEqual(diff.comments(), ["# increase price to 5%"])

    def test_diff_one_line_doc(self):
        diff = Diff(self.DIFF_ONE_LINE_DOC)
        self.assertEqual(diff.comments(), ['""" sort the list using quicksort algorithm """'])

    def test_diff_multi_line_doc(self):
        diff = Diff(self.DIFF_MULTI_LINE_DOC)
        expected_comment = '''""" sort the list using quicksort algorithm \n''' \
                            '''Second Line\n''' \
                            '''First Line\n''' \
                            '''\n''' \
                            '''"""'''
        self.assertEqual(diff.comments(), [expected_comment])

    def test_diff_bad(self):
        diff = Diff(self.DIFF_BAD)
        self.assertEqual(diff.comments(), [])

    def test_diff_multiple(self):
        diff = Diff(self.DIFF_MULTIPLE)
        expected_comment = []
        expected_comment.append('""" sort the list using quicksort algorithm """')
        expected_comment.append('# increase price to 5%')
        expected_comment.append('# increase price to 5%')
        self.assertEqual(diff.comments(), expected_comment)


if __name__ == '__main__':
    unittest.main()