import unittest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta

from app.analyzer import DatabaseService

class TestDatabaseService(unittest.TestCase):
    def setUp(self):
        self.session_mock = MagicMock()
        self.session_factory_mock = MagicMock(return_value=self.session_mock.__enter__.return_value)
        self.database_service = DatabaseService(session_factory=self.session_factory_mock)

    @patch('app.analyzer.func.avg', autospec=True)
    def test_calculate_avg(self, mock_avg):
        self.session_mock.query.return_value.filter.return_value.scalar.return_value = 10.0
        result = self.database_service.calculate_avg(self.session_mock, "KJFK", date.today() - timedelta(days=3), date.today())
        self.assertEqual(result, 10.0)

    def test_update_or_create(self):
        station_code = "KJFK"
        avg_visibility = 10.0
        self.database_service.update_or_create(self.session_mock, station_code, avg_visibility)
        self.assertTrue(self.session_mock.add.called or self.session_mock.query.return_value.filter_by.return_value.first.return_value is not None)

if __name__ == '__main__':
    unittest.main()