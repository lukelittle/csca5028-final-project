# import os
# import unittest
# from flask_testing import TestCase
# from app.run import app, db
# from app.models.three_day_avg_visibility import ThreeDayAverageVisibility


# class TestConfig:
#     TESTING = True
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False


# class TestRun(TestCase):

#     def create_app(self):
#         app.config.from_object(TestConfig)
#         return app

#     def setUp(self):
#         db.create_all()
#         db.session.add(ThreeDayAverageVisibility(station='TEST1', average_visibility=11.0))
#         db.session.commit()

#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()

#     def test_main_route(self):
#         response = self.client.get('/')
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue('text/html' in response.content_type)

#     def test_query_visibility_exists(self):
#         response = self.client.get('/query?station=TEST1')
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(b'10.0', response.data)

#     def test_query_visibility_no_station(self):
#         response = self.client.get('/query')
#         self.assertRedirects(response, '/')


# if __name__ == '__main__':
#     unittest.main()
