import unittest

from py_dot.core.lists import safe_insert, to_wrap_string, from_wrap_string


class TestLists(unittest.TestCase):
    def test_safe_insert1(self):
        target = []
        self.assertListEqual(
            safe_insert(target, 1, 1),
            [None, 1]
        )

    def test_safe_insert2(self):
        target = []
        self.assertListEqual(
            safe_insert(target, 2, 1),
            [None, None, 1]
        )

    def test_safe_insert3(self):
        target = [1]
        self.assertListEqual(
            safe_insert(target, 2, 1),
            [1, None, 1]
        )

    def test_to_wrap_string(self):
        self.assertEqual(
            to_wrap_string(['a', 'b', 'c'], '|'),
            '|a||b||c|'
        )

        self.assertEqual(
            to_wrap_string(
                ['a', 'b', 'c'],
                first_starts='{',
                separator=', ',
                last_ends='}'
            ),
            '{a, b, c}'
        )

    def test_from_wrap_string(self):
        self.assertListEqual(
            from_wrap_string('|a||b||c|', '|'),
            ['a', 'b', 'c']
        )

        self.assertListEqual(
            from_wrap_string(
                '{a, b, c}',
                first_starts='{',
                separator=', ',
                last_ends='}'
            ),
            ['a', 'b', 'c']
        )
