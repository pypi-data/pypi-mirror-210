from unittest import TestCase

from dead_code_finder.cli import main


class DeadCodeFinderTests(TestCase):
    def test_main(self):
        self.assertIsNone(main())
