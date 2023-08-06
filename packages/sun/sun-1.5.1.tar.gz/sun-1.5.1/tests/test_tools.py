import unittest
from sun.cli.tool import Tools


class TestTools(unittest.TestCase):

    def setUp(self):
        self.tools = Tools()

    def test_check_updates(self):
        self.assertEqual(('No news is good news!', []), self.tools.check_updates())

    def test_daemon_status(self):
        self.assertEqual(True, self.tools.daemon_status())

    def test_daemon_process(self):
        self.assertEqual('FAILED [1]: SUN is already running',
                         self.tools.daemon_process('start', 'Starting SUN daemon:  sun_daemon &'))


if __name__ == '__main__':
    unittest.main()
