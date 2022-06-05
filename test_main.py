import unittest
import requests


class TestCase(unittest.TestCase):

    base = "http://127.0.0.1:5000/"

    def test_hello_world(self):
        response = requests.get(self.base + 'helloworld' , {'name':'pouya', 'test':1})
        print (response)
        self.assertEqual(200, response.status_code)



if __name__ == '__main__':
    unittest.main()