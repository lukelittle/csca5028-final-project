import unittest
from unittest.mock import MagicMock, patch
import json
from app.collector import QueueService, DataCollector

class TestQueueService(unittest.TestCase):
    def setUp(self):
        self.mq_client_mock = MagicMock()
        self.queue_service = QueueService(self.mq_client_mock, "csca5028")

    def test_publish_message(self):
        test_message = {"key": "value"}
        self.queue_service.publish_message(test_message)
        self.mq_client_mock.queue.assert_called_with("csca5028")
        self.mq_client_mock.queue("csca5028").post.assert_called_with(test_message)

    def test_get_messages(self):
        self.queue_service.get_messages()
        self.mq_client_mock.queue.assert_called_with("csca5028")
        self.mq_client_mock.queue("csca5028").get.assert_called()

    def test_delete_message(self):
        test_message_id = "123"
        self.queue_service.delete_message(test_message_id)
        self.mq_client_mock.queue.assert_called_with("csca5028")
        self.mq_client_mock.queue("csca5028").delete.assert_called_with(test_message_id)

class TestDataCollector(unittest.TestCase):
    def setUp(self):
        self.queue_service_mock = MagicMock()
        self.db_session_mock = MagicMock()
        self.data_collector = DataCollector(self.queue_service_mock, self.db_session_mock)

    @patch('app.collector.DataCollector.get_visibility', return_value=10.0)
    def test_fetch_and_update_visibility_success(self, get_visibility_mock):
        station_code = "TEST_CODE"
        self.db_session_mock.query.return_value.filter_by.return_value.first.return_value = None
        self.data_collector.fetch_and_update_visibility(station_code)
        self.db_session_mock.add.assert_called()
        self.db_session_mock.commit.assert_called()
        self.queue_service_mock.publish_message.assert_called_with(json.dumps({'station_code': station_code}))

    @patch('app.collector.DataCollector.get_visibility', return_value=None)
    def test_fetch_and_update_visibility_none(self, get_visibility_mock):
        station_code = "TEST_CODE"
        self.data_collector.fetch_and_update_visibility(station_code)
        self.db_session_mock.add.assert_not_called()
        self.queue_service_mock.publish_message.assert_not_called()

if __name__ == '__main__':
    unittest.main()