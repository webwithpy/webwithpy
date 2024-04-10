from unittest import TestCase
import requests


class ServerTest(TestCase):
    def setUp(self):
        self.session = requests.Session()
