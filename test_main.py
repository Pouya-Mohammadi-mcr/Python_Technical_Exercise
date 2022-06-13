import unittest
import requests


class TestCase(unittest.TestCase):

    base = "http://0.0.0.0:80/"

    def setUp(self):
        pass

    def test_CLI_command(self):
        response = requests.get(self.base + "cli/sh ip int br")
        self.assertTrue('Interface' and 'IP-Address' and 'Status' and 'Method' 
                        and 'Protocol' in response.text)

    def test_CLI_other_commands(self):
        response = requests.get(self.base + "cli/show debugging")
        self.assertEqual(200, response.status_code)

    def test_CLI_inavlid_commands(self):
        response = requests.get(self.base + "cli/show sth")
        self.assertTrue('Line has invalid autocommand' in response.text)

    def test_invalid_endpoint(self):
        response = requests.get(self.base + "notfound/show debugging")
        self.assertEqual(404, response.status_code)

    def test_configure_loopback(self):
        response = requests.put(self.base + "loopback/1", {
                'description': 'test loopback',
                'ip_address': '10.1.1.1',
                'mask': '255.255.255.0'})
        self.assertTrue('ok' in response.text)

    def test_configure_loopback_no_description(self):
        response = requests.put(self.base + "loopback/3", {
                'no_description': 'test loopback',
                'ip_address': '10.1.1.1',
                'mask': '255.255.255.0'})
        self.assertTrue('Loopback description is required' in response.text)

    def test_configure_loopback_no_ip(self):
        response = requests.put(self.base + "loopback/3", {
                'description': 'test loopback',
                'no_ip_address': '10.1.1.1',
                'mask': '255.255.255.0'})
        self.assertTrue('Loopback ip_address is required' in response.text)

    def test_configure_loopback_no_mask(self):
        response = requests.put(self.base + "loopback/3", {
                'description': 'test loopback',
                'ip_address': '10.1.1.1',
                'no_mask': '255.255.255.0'})
        self.assertTrue('mask for the loopback is required' in response.text)

    def test_configure_loopback_invalid_ip_mask(self):
        response = requests.put(self.base + "loopback/3", {
                'description': 'test loopback',
                'ip_address': '1.1.1.1',
                'mask': '0.0.0.0'})
        self.assertEqual('"Inconsistent value"\n', response.text)

    def test_configure_loopback_dry_run(self):
        response = requests.put(self.base + "loopback/3", {
                    'dry_run': True,
                    'description': 'test loopback',
                    'ip_address': '10.1.1.1',
                    'mask': '255.255.255.0'})
        self.assertTrue('<config' in response.text)

    def test_delete_loopback(self):
        # Set-up the loopback to delete
        requests.put(self.base + "loopback/1", {
                    'description': 'test loopback',
                    'ip_address': '10.1.1.1',
                    'mask': '255.255.255.0'})
        response = requests.delete(self.base + "loopback/Loopback1")
        self.assertTrue('ok' in response.text)

    def test_delete_invalid_loopback(self):
        response = requests.delete(self.base + "loopback/Loopbackinvalid123")
        self.assertEqual('"Invalid loopback"\n',  response.text)

    def test_delete_loopback_dry_run(self):
        response = requests.delete(
                                self.base + "loopback/3",
                                data={'dry_run': True})
        self.assertTrue('<config' in response.text)

# Should be tested when credential are given by the user
#    def test_CLI_connection_failed(self):
#        response = requests.get(self.base + "cli/sh ip int br")
#        print (response.text)
#        self.assertEqual('"Connection failed"\n', response.text)


if __name__ == '__main__':
    unittest.main()
