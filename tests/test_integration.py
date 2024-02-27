# import unittest
# import app.app as app

# class FlaskAppTestCase(unittest.TestCase):

#     def setUp(self):
#         self.app = app
#         self.app.config['TESTING'] = True
#         self.client = self.app.test_client()

#     def test_main_route(self):
#         response = self.client.get('/')
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('list of possible station codes', response.data.decode('utf-8'))

# if __name__ == '__main__':
#     unittest.main()