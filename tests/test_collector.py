import unittest
from unittest.mock import MagicMock, patch
from typing import Any

from app.collector import DataCollector

class TestDataCollector(unittest.TestCase):
    @patch('app.collector.requests.get')
    def test_get_visibility(self, mock_get: MagicMock) -> None:

        mock_response: MagicMock = MagicMock()
        mock_response.json.return_value = {
            "properties": {
                "visibility": {"value": 10000}
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        visibility: float = DataCollector.get_visibility('FAKE_STATION_CODE')
        
        self.assertEqual(visibility, 10000)
