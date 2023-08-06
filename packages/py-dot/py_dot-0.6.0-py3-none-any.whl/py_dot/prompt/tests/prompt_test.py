import sys
import unittest

from py_dot.prompt import get_command_values


class TestPrompt(unittest.TestCase):
    def test_get_command_values(self):
        sys.argv = ['.py', '--foo=1', '--bar', '2']
        self.assertDictEqual(
            get_command_values(['foo', 'bar', 'baz']),
            {
                'foo': '1',
                'bar': '2'
            }
        )

        sys.argv = ['.py', '--foo', '1', '2', '--bar', '2']
        self.assertDictEqual(
            get_command_values(['foo', 'bar', 'baz']),
            {
                'foo': ['1', '2'],
                'bar': '2'
            }
        )
