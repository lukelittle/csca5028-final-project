# import unittest
# from unittest.mock import MagicMock, patch
# from typing import Any
# from app.analyzer import AverageVisibilityService
# from app.models.visibility_data import VisibilityData
# from app.models.three_day_avg_visibility import ThreeDayAverageVisibility

# class TestAverageVisibilityService(unittest.TestCase):
#     @patch('app.analyzer.AverageVisibilityService.Session')
#     @patch('app.analyzer.AverageVisibilityService.IronMQ')
#     def test_update_visibility_average(self, mock_ironmq: MagicMock, mock_session: MagicMock) -> None:

#         mock_session_factory: MagicMock = MagicMock()
#         mock_session.configure_mock(**{'return_value': mock_session_factory})

#         mock_session_factory.query.return_value.distinct.return_value = [
#             VisibilityData(station='STATION1'),
#             VisibilityData(station='STATION2')
#         ]

#         mock_session_factory.query.return_value.filter.return_value.scalar.side_effect = [10.5, 8.75]

#         service: AverageVisibilityService = AverageVisibilityService(mock_ironmq, 'test_queue', mock_session)

#         service.update_visibility_average()

#         self.assertEqual(mock_session_factory.query.call_count, 2)
#         self.assertEqual(mock_session_factory.commit.call_count, 1) 

#         args_list = mock_session_factory.add.call_args_list
#         self.assertEqual(len(args_list), 2) 

#         first_call_args: ThreeDayAverageVisibility = args_list[0][0][0]
#         self.assertIsInstance(first_call_args, ThreeDayAverageVisibility)
#         self.assertEqual(first_call_args.station, 'STATION1')
#         self.assertEqual(first_call_args.average_visibility, 10.5)

#         second_call_args: ThreeDayAverageVisibility = args_list[1][0][0]
#         self.assertIsInstance(second_call_args, ThreeDayAverageVisibility)
#         self.assertEqual(second_call_args.station, 'STATION2')
#         self.assertEqual(second_call_args.average_visibility, 8.75)

# if __name__ == '__main__':
#     unittest.main()