import unittest
import requests


class TestCase(unittest.TestCase):

    base = "http://127.0.0.1:5000/"

    def testCLI(self):
        response = requests.get(self.base + "cli/sh ip interface brief")
        print (response.json())
        self.assertEqual(200, response.status_code)

if __name__ == '__main__':
    unittest.main()