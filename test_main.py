import unittest
import requests


class TestCase(unittest.TestCase):

    base = "http://127.0.0.1:5000/"

    def test_CLI_interface(self):
        response = requests.get(self.base + "cli/sh ip int br")
        self.assertTrue('Interface' and 'IP-Address' and 'Status' and 'Method' and 'Protocol' in response.text)

    def test_CLI_other_commands(self):
        response = requests.get(self.base + "cli/show debugging")
        self.assertEqual(200, response.status_code)

    def test_CLI_inavlid_commands(self):
        response = requests.get(self.base + "cli/show sth")
        self.assertTrue('Line has invalid autocommand' in response.text)

    def test_invalid_endpoint(self):
        response = requests.get(self.base + "notfound/show debugging")
        self.assertEqual(404, response.status_code)

#Should be tested when credential are given by the user
#    def test_CLI_connection_failed(self):
#        response = requests.get(self.base + "cli/sh ip int br")
#        print (response.text)
#        self.assertEqual('"Connection failed"\n', response.text)

if __name__ == '__main__':
    unittest.main()