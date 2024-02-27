import os
import unittest
from datetime import datetime
from app.run import app, db, VisibilityData, ThreeDayAverageVisibility

class TestRun(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()

        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app = app.test_client()

        with app.app_context():
            db.create_all()
            sample_date = datetime.strptime('2022-01-01', '%Y-%m-%d').date()
            sample_data = VisibilityData(station='KJFK', date=sample_date, visibility=5.5)
            db.session.add(sample_data)
            db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_main_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_query_visibility_with_station(self):
        response = self.app.get('/query?station=KJFK')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'KJFK', response.data)

    def test_query_visibility_without_station(self):
        response = self.app.get('/query')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/' in response.location)

if __name__ == '__main__':
    unittest.main()