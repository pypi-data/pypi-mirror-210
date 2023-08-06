import json
import pytest
from os import environ, getenv
from dotenv import load_dotenv
from click.testing import CliRunner
import requests

load_dotenv()
USE_TESTERY_DEV = getenv('USE_TESTERY_DEV', 'False') == 'True'


@pytest.fixture()
def cli_runner():
    yield CliRunner()


@pytest.fixture(scope='session')
def url():
    if USE_TESTERY_DEV:
        yield 'https://api.dev.testery.io/api'
    else:
        yield 'https://api.testery.io/api'


@pytest.fixture(scope='session')
def token():
    yield environ['TESTERY_TOKEN']


@pytest.fixture(scope='session')
def fake_token():
    yield '123456abc'


@pytest.fixture(scope='session')
def environment():
    yield 'qa'


@pytest.fixture(scope='session')
def project():
    yield 'example-pytest-selenium'


@pytest.fixture(scope='session')
def test_runs():
    if USE_TESTERY_DEV:
        runs = {
            'pass': '189444',
            'fail': '192690',
            'canceled': '192454',
            'fail_with_ignored': '194402'
        }
    else:
        runs = {
            'pass': '290811',
            'fail': '297199',
            'canceled': '298578',
            'fail_with_ignored': '252467'
        }
    yield runs


@pytest.fixture()
def start_test_run(token, url, project, environment):
    test_run_request = {"project": project, "environment": environment}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    headers['Authorization'] = f"Bearer {token}"
    try:
        test_run_response = requests.post(
            f'{url}/test-run-requests-build',
            headers=headers,
            json=test_run_request
            )
        assert test_run_response.status_code == 201
        yield test_run_response.json()
    except Exception as e:
        raise f'Could not start test run: {e}'


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://api.testery.io/api/test-runs?limit=250&offset=0':
        with open('tests/testdata/mock_get_test_runs.json') as mock_json:
            response_json = json.load(mock_json)
            return MockResponse(response_json, 200)

    return MockResponse(None, 404)
