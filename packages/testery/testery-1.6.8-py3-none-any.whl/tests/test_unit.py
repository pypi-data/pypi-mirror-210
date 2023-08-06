from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from testery import list_active_test_runs, monitor_test_runs
from tests.conftest import mocked_requests_get


# TODO: add no running tests runs scenario
class TestMonitorTestRuns:

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_monitor_test_runs(self, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        expected_output = ("Test run 304098 is now RUNNING.\n"
                           "There are 4 tests passing out of 6 with 1 failing.\n"
                           "Test run 304090 is now SUBMITTED.\n"
                           "There are 4 tests passing out of 6 with 2 failing.\n")
        params = [f'--token={fake_token}', '--duration=0']

        result = cli_runner.invoke(monitor_test_runs, params)

        assert result.exit_code == 0
        assert result.output == expected_output
        mock_get.assert_called_once_with(
            'https://api.testery.io/api/test-runs?limit=250&offset=0',
            headers=expected_headers
        )


# TODO: add no running tests scenario
class TestGetTestRuns:

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_get_test_runs_pretty(self, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        params = [f'--token={fake_token}']

        result = cli_runner.invoke(list_active_test_runs, params)

        assert result.exit_code == 0
        assert result.output == '304098: RUNNING\n304090: SUBMITTED\n'
        mock_get.assert_called_once_with(
            'https://api.testery.io/api/test-runs?limit=250&offset=0',
            headers=expected_headers
        )

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_get_test_runs_json(self, mock_get: MagicMock, fake_token: str, cli_runner: CliRunner):
        expected_headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {fake_token}'
        }
        params = [f'--token={fake_token}', '--output=json']

        result = cli_runner.invoke(list_active_test_runs, params)

        assert result.exit_code == 0
        assert result.output == '{"304098": "RUNNING", "304090": "SUBMITTED"}\n'
        mock_get.assert_called_once_with(
            'https://api.testery.io/api/test-runs?limit=250&offset=0',
            headers=expected_headers
        )
