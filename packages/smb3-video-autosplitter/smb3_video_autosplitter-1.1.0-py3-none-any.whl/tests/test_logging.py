import unittest

from smb3_video_autosplitter import logging


class TestLogging(unittest.TestCase):
    def test_initialize_logging(self):
        logging.initialize_logging()
