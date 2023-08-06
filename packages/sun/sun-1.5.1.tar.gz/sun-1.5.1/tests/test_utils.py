import unittest
from pathlib import Path
from sun.utils import Utilities, Fetch


class TestTools(unittest.TestCase, Utilities):

    def setUp(self):
        super(Utilities, self).__init__()
        self.fetch = Fetch()

    def test_read_repo_text_file(self):
        self.assertGreater(len(self.read_repo_text_file(
            'https://mirrors.slackware.com/slackware/slackware64-15.0/ChangeLog.txt')), 10)

    def test_read_local_text_file(self):
        self.assertGreater(len(self.read_local_text_file(Path('/var/lib/slackpkg/ChangeLog.txt'))), 10)

    def test_slack_version(self):
        self.assertTrue('Slackware', self.slack_version()[0])
        self.assertTrue('15.0', self.slack_version()[1])

    def test_fetch_updates(self):
        self.assertEqual([], list(self.fetch.updates()))


if __name__ == '__main__':
    unittest.main()
