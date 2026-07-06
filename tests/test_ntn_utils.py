import os
import boto3
import pytest
import pendulum
import requests
import pandas as pd
import src.ntn_utils as ntn_utils
from unittest.mock import call
from sqlalchemy.exc import SQLAlchemyError


filter_cols = ['Name', 'Архивирай']

@pytest.fixture
def mock_notion_json_full():

    json_full = {
        "object": "list",
        "results": [
            {
                "object": "page",
                "id": "mock_id",
                "created_time": "2023-03-01T15:37:00.000Z",
                "last_edited_time": "2023-03-01T15:37:00.000Z",
                "created_by": {"object": "user", "id": "mock_id"},
                "last_edited_by": {"object": "user", "id": "mock_id"},
                "cover": "null",
                "icon": {"type": "emoji", "emoji": "🚨"},
                "parent": {"type": "database_id", "database_id": "mock_id"},
                "in_trash": False,
                "is_archived": False,
                "is_locked": False,
                "properties": {
                    "Архивирай": {"id": "NiYw", "type": "checkbox", "checkbox": False},
                    "Приходи": {
                        "id": "mock_id",
                        "type": "rollup",
                        "rollup": {"type": "number", "number": "null", "function": "sum"},
                    },
                    "Приходи (трансфери)": {
                        "id": "mock_id",
                        "type": "rollup",
                        "rollup": {"type": "number", "number": "null", "function": "sum"},
                    },
                    "Разходи (трансфери)": {
                        "id": "mock_id",
                        "type": "rollup",
                        "rollup": {"type": "number", "number": "null", "function": "sum"},
                    },
                    "Разходи": {
                        "id": "mock_id",
                        "type": "rollup",
                        "rollup": {"type": "number", "number": "null", "function": "sum"},
                    },
                    "Наличност": {
                        "id": "mock_id",
                        "type": "rollup",
                        "rollup": {"type": "number", "number": 1, "function": "sum"},
                    },
                    "Подкатегории": {
                        "id": "mock_id",
                        "type": "relation",
                        "relation": [
                            {"id": "mock_id"},
                            {"id": "mock_id"},
                        ],
                        "has_more": False,
                    },
                    "Name": {
                        "id": "mock_id",
                        "type": "title",
                        "title": [
                            {
                                "type": "text",
                                "text": {"content": "Авариен фонд", "link": "null"},
                                "annotations": {
                                    "bold": False,
                                    "italic": False,
                                    "strikethrough": False,
                                    "underline": False,
                                    "code": False,
                                    "color": "default",
                                },
                                "plain_text": "Авариен фонд",
                                "href": "null",
                            }
                        ],
                    },
                },
                "url": "mock_url",
                "public_url": "null",
                "archived": False,
            }
        ],
        "next_cursor": "null",
        "has_more": False,
        "type": "page_or_database",
        "page_or_database": {},
        "request_id": "mock_id",
    }

    return json_full

@pytest.fixture
def mock_notion_json_filtered():

    json_filtered = {
        "object": "list",
        "results": [
            {
                "object": "page",
                "id": "mock_id",
                "created_time": "2023-03-01T15:37:00.000Z",
                "last_edited_time": "2023-03-01T15:37:00.000Z",
                "created_by": {"object": "user", "id": "mock_id"},
                "last_edited_by": {"object": "user", "id": "mock_id"},
                "cover": "null",
                "icon": {"type": "emoji", "emoji": "🚨"},
                "parent": {"type": "database_id", "database_id": "mock_id"},
                "in_trash": False,
                "is_archived": False,
                "is_locked": False,
                "properties": {
                    "Архивирай": {"id": "NiYw", "type": "checkbox", "checkbox": False},
                    "Name": {
                        "id": "mock_id",
                        "type": "title",
                        "title": [
                            {
                                "type": "text",
                                "text": {"content": "Авариен фонд", "link": "null"},
                                "annotations": {
                                    "bold": False,
                                    "italic": False,
                                    "strikethrough": False,
                                    "underline": False,
                                    "code": False,
                                    "color": "default",
                                },
                                "plain_text": "Авариен фонд",
                                "href": "null",
                            }
                        ],
                    },
                },
                "url": "mock_url",
                "public_url": "null",
                "archived": False,
            }
        ],
        "next_cursor": "null",
        "has_more": False,
        "type": "page_or_database",
        "page_or_database": {},
        "request_id": "mock_id",
    }

    return json_filtered

@pytest.fixture
def mock_notion_json_pagination():

    json_paged = {
        "object": "list",
        "results": [
            {
                "object": "page",
                "id": "mock_id",
                "created_time": "2023-03-01T15:37:00.000Z",
                "last_edited_time": "2023-03-01T15:37:00.000Z",
                "created_by": {"object": "user", "id": "mock_id"},
                "last_edited_by": {"object": "user", "id": "mock_id"},
                "cover": "null",
                "icon": {"type": "emoji", "emoji": "🚨"},
                "parent": {"type": "database_id", "database_id": "mock_id"},
                "in_trash": False,
                "is_archived": False,
                "is_locked": False,
                "properties": {
                    "Архивирай": {"id": "NiYw", "type": "checkbox", "checkbox": False},
                    "Name": {
                        "id": "mock_id",
                        "type": "title",
                        "title": [
                            {
                                "type": "text",
                                "text": {"content": "Авариен фонд", "link": "null"},
                                "annotations": {
                                    "bold": False,
                                    "italic": False,
                                    "strikethrough": False,
                                    "underline": False,
                                    "code": False,
                                    "color": "default",
                                },
                                "plain_text": "Авариен фонд",
                                "href": "null",
                            }
                        ],
                    },
                },
                "url": "mock_url",
                "public_url": "null",
                "archived": False,
            },
            {
                "object": "page",
                "id": "mock_id",
                "created_time": "2023-03-01T15:37:00.000Z",
                "last_edited_time": "2023-03-01T15:37:00.000Z",
                "created_by": {"object": "user", "id": "mock_id"},
                "last_edited_by": {"object": "user", "id": "mock_id"},
                "cover": "null",
                "icon": {"type": "emoji", "emoji": "🚨"},
                "parent": {"type": "database_id", "database_id": "mock_id"},
                "in_trash": False,
                "is_archived": False,
                "is_locked": False,
                "properties": {
                    "Архивирай": {"id": "NiYw", "type": "checkbox", "checkbox": False},
                    "Name": {
                        "id": "mock_id",
                        "type": "title",
                        "title": [
                            {
                                "type": "text",
                                "text": {"content": "Авариен фонд", "link": "null"},
                                "annotations": {
                                    "bold": False,
                                    "italic": False,
                                    "strikethrough": False,
                                    "underline": False,
                                    "code": False,
                                    "color": "default",
                                },
                                "plain_text": "Авариен фонд",
                                "href": "null",
                            }
                        ],
                    },
                },
                "url": "mock_url",
                "public_url": "null",
                "archived": False,
            }
        ],
        "next_cursor": "null",
        "has_more": False,
        "type": "page_or_database",
        "page_or_database": {},
        "request_id": "mock_id",
    }

    return json_paged

@pytest.fixture
def fake_environment_lookup():
    """
    Return a function that simulates os.getenv() for testing purposes.
    We have to define a function inside the fixture because pytest fixtures cannot return a dictionary directly.
    """

    def lookup(key):
         env_dictionary = {
             "NOTION_API_KEY": "fake_api_key",
             'POSTGRES_DB': 'fake_postgres_db_key',
             'POSTGRES_USER': 'fake_postgres_user_key',
             'POSTGRES_PASSWORD': 'fake_postgres_pass_key',
             'POSTGRES_HOST': 'fake_postgres_host_key',
             'NOTION_DB_ID_YEAR': 'fake_ntn_year_key',
             'NOTION_DB_ID_MONTH': 'fake_ntn_month_key',
             'NOTION_DB_ID_CATEGORY': 'fake_ntn_category_key',
             'NOTION_DB_ID_SUBCATEGORY': 'fake_ntn_subcategory_key',
             'NOTION_DB_ID_BUDGET': 'fake_ntn_budget_key',
             'NOTION_DB_ID_ACCOUNT': 'fake_ntn_account_key',
             'NOTION_DB_ID_TRANSACTION': 'fake_ntn_transaction_key',
             'S3_BUCKET_NAME': 'fake_s3_key',
         }
         return env_dictionary.get(key)

    return lookup


def test_get_data_return_value_filtered(mocker, mock_notion_json_filtered, fake_environment_lookup):
    """
    Test if get_data()'s return value all_data matches expectations
    with FILTERED API response.
    """

    # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Mock the response of the API client
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_notion_json_filtered

    # Set the mock API client to return the mocked response
    mock_post.return_value = mock_response

    # Call the function with the mock API client
    result = ntn_utils.get_data('fake_ntn_account_key', pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC'), filter_cols)

    # Assert that the correct data is returned
    assert result == mock_notion_json_filtered['results']

    # Assert the number of times mocks were called
    assert mock_post.call_count == 1
    assert mock_sleep.call_count == 1
    assert mock_getenv.call_count == 3


def test_get_data_return_value_no_filter(mocker, mock_notion_json_full, fake_environment_lookup):
    """
    Test if get_data()'s return value all_data matches expectations
    with FULL API response.
    """

     # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Mocke the response of the API client
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_notion_json_full

    # Set the mock API client to return the mocked response
    mock_post.return_value = mock_response

    # Call the function with the mock API client
    result = ntn_utils.get_data('fake_ntn_account_key', pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC'), filter_cols=[])

    # Assert that the correct data is returned
    assert result == mock_notion_json_full['results']

    # Assert the number of times mocks were called
    assert mock_post.call_count == 1
    assert mock_sleep.call_count == 1
    assert mock_getenv.call_count == 3


def test_get_data_raises_exception_on_non_200(mocker, fake_environment_lookup):
    """Test if function raises an exception when the API response is not 200."""

    # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Mock the response of the API client
    mock_response = mocker.MagicMock()
    mock_response.status_code = 500  # Simulate a server error

    # Use 'side_effect' instead of 'return_value' for raising exceptions
    mock_error = requests.exceptions.HTTPError("500 Server Error")
    mock_response.raise_for_status.side_effect = mock_error

    # Set the mock API client to return the mocked response
    mock_post.return_value = mock_response

    # Call the function and assert that it raises an exception
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        ntn_utils.get_data('fake_ntn_account_key', pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC'), filter_cols)

    # Assert the exception contains the expected message.
    assert "500 Server Error" == str(exc_info.value)

    # Assert the number of times mocks were called
    assert mock_post.call_count == 1
    assert mock_sleep.call_count == 0
    assert mock_getenv.call_count == 3


def test_get_data_retries_and_fails_on_constant_429(mocker, fake_environment_lookup):
    """
    Test if get_data() raises an exception when the API response is 429,
    retries 3 times and fail on all of them.
    """

    # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Mock the response of the API client
    mock_429 = mocker.MagicMock()
    mock_429.status_code = 429  # Simulate rate_limited
    mock_429.raise_for_status.side_effect = requests.exceptions.HTTPError('Rate limited.')

    # Pass a list of mock statuses for all 3 exec attempts
    mock_post.side_effect = [mock_429, mock_429, mock_429]

    # Call the function and assert that it raises an exception
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        ntn_utils.get_data('fake_ntn_account_key', pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC'), filter_cols)

    # Assert the exception contains the expected message.
    assert "Rate limited." == str(exc_info.value)

    # Assert the number of times mocks were called
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2
    assert mock_getenv.call_count == 3


def test_get_data_recovers_after_retries(mocker, mock_notion_json_filtered, fake_environment_lookup):
    """
    Test if get_data() raises an exception when the API response is 429,
    retries 2 times and fails, but succeed on the 3-rd retry.
    """

    # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Mock the 429 response of the API client
    mock_429 = mocker.MagicMock()
    mock_429.status_code = 429  # Simulate rate_limited
    mock_429.raise_for_status.side_effect = requests.exceptions.HTTPError('Rate limited.')

    # Mock the 200 response of the API client
    mock_200 = mocker.MagicMock()
    mock_200.status_code = 200  # Success
    mock_200.json.return_value = mock_notion_json_filtered

    # Pass a list of mock statuses for all 3 exec attempts
    mock_post.side_effect = [mock_429, mock_429, mock_200]

    # Call the function with the mock API client
    result = ntn_utils.get_data('fake_ntn_account_key', pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC'), filter_cols)

    # Assert that the correct data is returned
    assert result == mock_notion_json_filtered['results']

    # Assert the loop ran exactly 3 times before succeeding
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 3  # 2 in the while loop and 1 in the end of script
    assert mock_getenv.call_count == 3

    # Assert that the sleep is in the right order and in the right amount
    expected_sleep_history = [
        call(20),  # First retry delay
        call(20),  # Second retry delay
        call(0.5)  # Final success delay
    ]

    assert mock_sleep.call_args_list == expected_sleep_history


def test_get_data_retries_and_fails_on_network_issues(mocker, fake_environment_lookup):
    """
    Test if get_data() raises an exception when we have RequestException,
    due to network issues.
    """

    # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Mock the response of the API client
    mock_429 = mocker.MagicMock()
    mock_429.status_code = 429  # Simulate rate_limited
    mock_429.raise_for_status.side_effect = requests.exceptions.RequestException('Network issue.')

    # Pass a list of mock statuses for all 3 exec attempts
    mock_post.side_effect = [mock_429, mock_429, mock_429]

    # Call the function and assert that it raises an exception
    with pytest.raises(requests.exceptions.RequestException) as exc_info:
        ntn_utils.get_data('fake_ntn_account_key', pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC'), filter_cols)

    # Assert the exception contains the expected message.
    assert "Network issue." == str(exc_info.value)

    # Assert the number of times mocks were called
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2
    assert mock_getenv.call_count == 3


def test_get_data_pagination(mocker, mock_notion_json_filtered, mock_notion_json_pagination, fake_environment_lookup):
    """Test if pagination in get_data() works properly."""

    # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Create API response mock - first page
    mock_first_response = mocker.MagicMock()
    mock_first_response.status_code = 200
    mock_first_response.json.return_value = {"results": mock_notion_json_filtered['results'],
                                             "next_cursor": "null",
                                             "has_more": True,
                                             "type": "page_or_database",
                                             "page_or_database": {},
                                             "request_id": "mock_id"}

    # Create API response mock - second/last page
    mock_second_response = mocker.MagicMock()
    mock_second_response.status_code = 200
    mock_second_response.json.return_value = {"results": mock_notion_json_filtered['results'],
                                             "next_cursor": "null",
                                             "has_more": False,
                                             "type": "page_or_database",
                                             "page_or_database": {},
                                             "request_id": "mock_id"}

    # Simulate two sequential API responses:
    # First with has_more = True; Second with has_more = False
    mock_post.side_effect = [mock_first_response, mock_second_response]

    # Call the source function
    result = ntn_utils.get_data('fake_ntn_account_key', pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC'), filter_cols)

    assert result == mock_notion_json_pagination['results']

    # Assert the number of times mocks were called
    assert mock_post.call_count == 2
    assert mock_sleep.call_count == 2
    assert mock_getenv.call_count == 5


def test_get_data_reduce_payload_page_size(mocker, mock_notion_json_filtered, fake_environment_lookup):
    """Test if page_size is lowered from 100 to 25 when Notion database is Subcategory"""

    # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Mock the response of the API client
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_notion_json_filtered

    # Set the mock API client to return the mocked response
    mock_post.return_value = mock_response

    result = ntn_utils.get_data('fake_ntn_subcategory_key', pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC'), filter_cols)

    # Assert that the passed arguments to the API contain page_size = 25
    mock_post.assert_called_once_with(
        mocker.ANY,  # Using wildcard because the test is strictly for the page_size
        json={
            'page_size': 25,  # What we are testing for
            'filter': mocker.ANY,
        },
        headers=mocker.ANY,
        timeout=mocker.ANY
    )

    # Assert that the final result is correct
    assert result == mock_notion_json_filtered['results']


def test_get_data_add_filters_when_transaction(mocker, mock_notion_json_filtered, fake_environment_lookup):
    """Test if filters are added to the payload when Notion database is Transaction"""

    # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Mock the response of the API client
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_notion_json_filtered

    # Set the mock API client to return the mocked response
    mock_post.return_value = mock_response

    result = ntn_utils.get_data('fake_ntn_transaction_key', pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC'), filter_cols)

    # Assert that the passed arguments to the API contain filter for Template and Статус
    mock_post.assert_called_once_with(
        mocker.ANY,  # Using wildcard because the test is strictly for the page_size
        json={
            'page_size': 100,
            'filter': {
                'and': [
                    {'timestamp': 'last_edited_time', 'last_edited_time': {'after': '2020-01-01T18:00:00+00:00'}},
                    {
                        'and': [
                            {'property': 'Template', 'checkbox': {'does_not_equal': True}},
                            {'property': 'Статус', 'select': {'does_not_equal': 'Предстои'}},
                        ]
                    },
                ]
            },
        },
        headers=mocker.ANY,
        timeout=mocker.ANY,
    )

    # Assert that the final result is correct
    assert result == mock_notion_json_filtered['results']


def test_get_data_no_filters_when_last_load_date_is_none(mocker, mock_notion_json_filtered, fake_environment_lookup):
    """Test that no date filters are appended to the payload when doing a full load (last_load_date is None)."""

    # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Mock the response of the API client
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_notion_json_filtered

    # Set the mock API client to return the mocked response
    mock_post.return_value = mock_response

    result = ntn_utils.get_data('fake_ntn_subcategory_key', last_load_date=None, filter_cols=filter_cols)

    # Grab the payload sent to requests.post
    sent_payload = mock_post.call_args.kwargs["json"]

    # Assert that 'filter' was never added to the dictionary payload
    assert "filter" not in sent_payload


def test_get_data_api_network_error(mocker, mock_notion_json_filtered, fake_environment_lookup):
    """Test if get_data() raises the correct exception when the API returns a network error."""

    # Intercept source functions
    mock_post = mocker.patch("src.ntn_utils.requests.post")
    mock_getenv = mocker.patch("src.ntn_utils.os.getenv")
    mock_sleep = mocker.patch("src.ntn_utils.time.sleep")

    # Mock the response of getenv
    mock_getenv.side_effect = fake_environment_lookup

    # Mock the response of the API client
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException('Network error.')

    # Set the mock API client to return the mocked response
    mock_post.return_value = mock_response

    with pytest.raises(requests.exceptions.RequestException) as exc_info:
        ntn_utils.get_data('fake_ntn_account_key', pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC'), filter_cols)


def test_get_last_load_date(mocker):
    """Test if get_last_load_date() returns the correct date."""

    # Intercept source functions
    mock_pd_read_sql = mocker.patch("src.ntn_utils.pd.read_sql_query")

    # Mock the response of pd.read_sql
    mock_pd_read_sql.return_value = pd.DataFrame([{'last_load_date': pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC')}])

    # Call the function with the mock API client
    result = ntn_utils.get_last_load_date('mock_schema', 'mock_table', 'mock_engine')

    # Assert that the correct data is returned
    assert result == pendulum.datetime(2020, 1, 1, 18, 0, 0, tz='UTC')

    # Assert the number of times mocks were called
    assert mock_pd_read_sql.call_count == 1


def test_get_last_load_date_query_error(mocker):
    """
    Test if get_last_load_date() raises an exception when pd.read_sql_query() fails.
    """

    # Intercept source functions
    mock_pd_read_sql = mocker.patch("src.ntn_utils.pd.read_sql_query")

    # Mock the database response
    mock_pd_read_sql.side_effect = pd.errors.DatabaseError('DB Error')

    # Call the function and assert that it raises an exception
    with pytest.raises(pd.errors.DatabaseError) as exc_info:
        ntn_utils.get_last_load_date('mock_schema', 'mock_table', 'mock_engine')

    # Assert the exception contains the expected message.
    assert "DB Error" == str(exc_info.value)


def test_get_last_load_date_none(mocker):
    """Test if get_last_load_date() returns None when no previous loads are found."""

    # Intercept source functions
    mock_pd_read_sql = mocker.patch("src.ntn_utils.pd.read_sql_query")

    # Mock the response of pd.read_sql
    mock_pd_read_sql.return_value = pd.DataFrame([{'max(last_load_date)': None}])

    # Call the function with the mock API client
    result = ntn_utils.get_last_load_date('mock_schema', 'mock_table', 'mock_engine')

    # Assert that the correct data is returned
    assert result == None

    # Assert the number of times mocks were called
    assert mock_pd_read_sql.call_count == 1


def test_load_new_data(mocker):
    """Test successful deletion and insertion of new data."""

    # Create the input DataFrame
    new_data_df = pd.DataFrame(
        [
            {
                'id': 'mock_id',
                'title': 'mock_title',
                'is_archived': False,
                'created_time': '2023-03-01T15:37:00.000Z',
                'last_edited_time': '2023-03-01T15:37:00.000Z',
                'load_date': '2026-06-30T19:00:00.000Z',
            },
            {
                'id': 'mock_id_2',
                'title': 'mock_title_2',
                'is_archived': False,
                'created_time': '2024-03-01T15:37:00.000Z',
                'last_edited_time': '2024-03-01T15:37:00.000Z',
                'load_date': '2026-07-01T19:00:00.000Z',
            },
        ]
    )

    # Mock the database engine and the connection inside the 'with' block
    mock_engine = mocker.MagicMock()
    mock_conn = mocker.MagicMock()

    # Teach the engine how to behave when 'with engine.begin() as conn:' is called
    mock_engine.begin.return_value.__enter__.return_value = mock_conn

    # Intercept the pandas to_sql method
    mock_to_sql = mocker.patch.object(pd.DataFrame, 'to_sql')
    mock_to_sql.return_value = 2  # Simulate returning the number of rows inserted

    # Call the function
    result = ntn_utils.load_new_data('mock_schema', 'mock_table', new_data_df, mock_engine)

    # Assert the final result
    assert result == 2

    # Assert the DELETE query was executed correctly
    assert mock_conn.execute.call_count == 1

    # Extract the exact arguments passed to mock_conn.execute()
    args, kwargs = mock_conn.execute.call_args
    executed_query = str(args[0])
    executed_params = args[1]

    assert "DELETE from mock_schema.mock_table where id in :id_list" in executed_query
    assert executed_params == {'id_list': ('mock_id', 'mock_id_2')}

    # Assert the INSERT (to_sql) was executed correctly
    mock_to_sql.assert_called_once_with(
        name='mock_table',
        con=mock_conn,
        schema='mock_schema',
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )


def test_load_new_data_no_new_data(mocker):
    """
    Test the behavior of load_new_data() when the input DataFrame is empty (no new data to insert).
    """

    # Create the input DataFrame
    new_data_df = pd.DataFrame([])  # Empty DataFrame

    # Mock the database engine and the connection inside the 'with' block
    mock_engine = mocker.MagicMock()
    mock_conn = mocker.MagicMock()

    # Teach the engine how to behave when 'with engine.begin() as conn:' is called
    mock_engine.begin.return_value.__enter__.return_value = mock_conn

    # Call the function
    result = ntn_utils.load_new_data('mock_schema', 'mock_table', new_data_df, mock_engine)

    # Assert the final result
    assert result == 0  # No rows inserted since the DataFrame is empty


def test_load_new_data_db_error(mocker):
    """
    Test the behavior of load_new_data() when there is a database error.
    """

    # Create the input DataFrame
    new_data_df = pd.DataFrame(
        [
            {
                'id': 'mock_id',
                'title': 'mock_title',
                'is_archived': False,
                'created_time': '2023-03-01T15:37:00.000Z',
                'last_edited_time': '2023-03-01T15:37:00.000Z',
                'load_date': '2026-06-30T19:00:00.000Z',
            },
            {
                'id': 'mock_id_2',
                'title': 'mock_title_2',
                'is_archived': False,
                'created_time': '2024-03-01T15:37:00.000Z',
                'last_edited_time': '2024-03-01T15:37:00.000Z',
                'load_date': '2026-07-01T19:00:00.000Z',
            },
        ]
    )

    # Mock the database engine and the connection inside the 'with' block
    mock_engine = mocker.MagicMock()
    mock_conn = mocker.MagicMock()

    # Teach the engine how to behave when 'with engine.begin() as conn:' is called
    mock_engine.begin.return_value.__enter__.return_value = mock_conn

    # Intercept the pandas to_sql method
    mock_conn_exe = mocker.patch.object(mock_conn, 'execute')

    # Mock the database response
    mock_conn_exe.side_effect = pd.errors.DatabaseError('DB Error')

    # Call the function and assert that it raises an exception
    with pytest.raises(pd.errors.DatabaseError) as exc_info:
        ntn_utils.load_new_data('mock_schema', 'mock_table', new_data_df, mock_engine)

    # Assert the exception contains the expected message.
    assert "DB Error" == str(exc_info.value)

    # Extract the exact arguments passed to mock_conn.execute()
    args, kwargs = mock_conn.execute.call_args
    executed_query = str(args[0])
    executed_params = args[1]

    assert "DELETE from mock_schema.mock_table where id in :id_list" in executed_query
    assert executed_params == {'id_list': ('mock_id', 'mock_id_2')}


def test_del_missing_data_success(mocker):
    """Test successful deletion of missing data."""

    # Create the input DataFrame
    filtered_df = pd.DataFrame(
        [
            {
                'id': 'mock_id',
                'title': 'mock_title',
                'is_archived': False,
                'created_time': '2023-03-01T15:37:00.000Z',
                'last_edited_time': '2023-03-01T15:37:00.000Z',
                'load_date': '2026-06-30T19:00:00.000Z',
            },
            {
                'id': 'mock_id_2',
                'title': 'mock_title_2',
                'is_archived': False,
                'created_time': '2024-03-01T15:37:00.000Z',
                'last_edited_time': '2024-03-01T15:37:00.000Z',
                'load_date': '2026-07-01T19:00:00.000Z',
            },
        ]
    )

    # Mock the database engine and the connection inside the 'with' block
    mock_engine = mocker.MagicMock()
    mock_conn = mocker.MagicMock()

    # Teach the engine how to behave when 'with engine.begin() as conn:' is called
    mock_engine.begin.return_value.__enter__.return_value = mock_conn

    # Simulate returning the number of ID rows deleted
    mock_conn.execute.return_value.rowcount = 2

    # Intercept the pandas to_sql method
    mock_to_sql = mocker.patch.object(pd.DataFrame, 'to_sql')
    mock_to_sql.return_value = 2  # Simulate returning the number of rows inserted

    # Call the function
    result = ntn_utils.del_missing_data('mock_schema', 'mock_table', filtered_df, mock_engine)

    # Assert the final result
    assert result == 2

    # Assert the DELETE query was executed correctly
    assert mock_conn.execute.call_count == 2

    # Extract the exact arguments passed to mock_conn.execute()
    args, kwargs = mock_conn.execute.call_args
    executed_query = str(args[0])

    assert (
        "DELETE from mock_schema.mock_table t where not exists (select 1 from mock_schema.notion_ids_audit tt where tt.id = t.id and tt.source_name = 'mock_table')"
        in executed_query
    )

    # Assert the INSERT (to_sql) was executed correctly
    mock_to_sql.assert_called_once_with(
        name='notion_ids_audit',
        con=mock_conn,
        schema='mock_schema',
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )


def test_del_missing_data_exception(mocker):
    """Test exception handling during deletion of missing data."""

    # Create the input DataFrame
    filtered_df = pd.DataFrame(
        [
            {
                'id': 'mock_id',
                'title': 'mock_title',
                'is_archived': False,
                'created_time': '2023-03-01T15:37:00.000Z',
                'last_edited_time': '2023-03-01T15:37:00.000Z',
                'load_date': '2026-06-30T19:00:00.000Z',
            },
            {
                'id': 'mock_id_2',
                'title': 'mock_title_2',
                'is_archived': False,
                'created_time': '2024-03-01T15:37:00.000Z',
                'last_edited_time': '2024-03-01T15:37:00.000Z',
                'load_date': '2026-07-01T19:00:00.000Z',
            },
        ]
    )

    # Mock the database engine and the connection inside the 'with' block
    mock_engine = mocker.MagicMock()
    mock_conn = mocker.MagicMock()

    # Teach the engine how to behave when 'with engine.begin() as conn:' is called
    mock_engine.begin.return_value.__enter__.return_value = mock_conn

    # Simulate returning the number of ID rows deleted
    mock_conn.execute.side_effect = pd.errors.DatabaseError('DB Error')

    # Call the function and assert that it raises an exception
    with pytest.raises(pd.errors.DatabaseError) as exc_info:
        ntn_utils.del_missing_data('mock_schema', 'mock_table', filtered_df, mock_engine)

    # Assert the exception contains the expected message.
    assert "DB Error" == str(exc_info.value)


def test_upsert_into_stats_insert_stmt(mocker):
    """Test the behavior of upsert_into_stats() when inserting a new record."""

    mock_engine = mocker.MagicMock()
    mock_conn = mocker.MagicMock()

    mock_engine.begin.return_value.__enter__.return_value = mock_conn

    mock_conn.execute.return_value.fetchone.return_value = None

    ntn_utils.upsert_into_stats(
        mock_engine, 'mock_row_count', 'mock_run_id', 'mock_run_date', 'mock_dag_name', 'mock_task_name', 'ntn_extracted'
    )

    # Assert the DELETE query was executed correctly
    assert mock_conn.execute.call_count == 2

    # Extract the history of what queries were sent
    all_calls = mock_conn.execute.call_args_list

    select_query = str(all_calls[0][0][0])
    insert_query = str(all_calls[1][0][0])

    assert "SELECT" in select_query
    assert "INSERT" in insert_query


def test_upsert_into_stats_update_stmt(mocker):
    """Test the behavior of upsert_into_stats() when updating an existing record."""

    mock_engine = mocker.MagicMock()
    mock_conn = mocker.MagicMock()

    mock_engine.begin.return_value.__enter__.return_value = mock_conn

    mock_conn.execute.return_value.fetchone.return_value = ('mock_id', 'mock_date')

    ntn_utils.upsert_into_stats(
        mock_engine, 'mock_row_count', 'mock_run_id', 'mock_run_date', 'mock_dag_name', 'mock_task_name', 'ntn_extracted'
    )

    # Assert the DELETE query was executed correctly
    assert mock_conn.execute.call_count == 2

    # Extract the history of what queries were sent
    all_calls = mock_conn.execute.call_args_list

    select_query = str(all_calls[0][0][0])
    insert_query = str(all_calls[1][0][0])

    assert "SELECT" in select_query
    assert "UPDATE" in insert_query


def test_upsert_into_stats_exception(mocker):
    """Test the behavior of upsert_into_stats() when there is a database error."""

    mock_engine = mocker.MagicMock()
    mock_conn = mocker.MagicMock()

    mock_engine.begin.return_value.__enter__.return_value = mock_conn

    mock_conn.execute.side_effect = SQLAlchemyError('DB Error')

    with pytest.raises(SQLAlchemyError) as exc_info:
        ntn_utils.upsert_into_stats(
            mock_engine, 'mock_row_count', 'mock_run_id', 'mock_run_date', 'mock_dag_name', 'mock_task_name', 'ntn_extracted'
        )

    # Assert the exception contains the expected message.
    assert "DB Error" == str(exc_info.value)


def test_upload_to_s3_empty_df(mocker):
    """Test the behavior of upload_to_s3() when the DataFrame is empty."""

    # Intercept the boto3 S3 client
    mock_s3_upload = mocker.patch('src.ntn_utils.boto3.client')

    # Mock the S3 upload_fileobj method to simulate a successful upload
    mock_s3_upload.return_value = 'Fake object'

    # Create an empty DataFrame
    mock_df = pd.DataFrame([])

    # Call the function
    result = ntn_utils.upload_to_s3(mock_df, 'mock_bucket_name', 'mock_file_name')

    # Assert that the function returns None for an empty DataFrame
    assert result == None

    # Assert that the S3 upload_fileobj method was not called since the DataFrame is empty
    mock_s3_upload.assert_not_called()


def test_upload_to_s3_success(mocker):
    """Test the behavior of upload_to_s3() when the DataFrame is not empty."""

    # Intercept the boto3 S3 client
    mock_s3_boto = mocker.patch('src.ntn_utils.boto3.client')

    # Create an empty DataFrame
    mock_df = pd.DataFrame([{'id': 'mock_id', 'title': 'mock_title'}])

    # Call the function
    ntn_utils.upload_to_s3(mock_df, 'mock_bucket_name', 'mock_file_name')

    # Assert that the S3 put_object method was called with the correct parameters
    mock_s3_boto.return_value.put_object.assert_called_once_with(
        Bucket='mock_bucket_name',
        Key='mock_file_name',
        Body=mocker.ANY  # We can use ANY since we don't care about the exact content of the CSV in this test
    )


def test_upload_to_s3_exception(mocker):
    """Test the behavior of upload_to_s3() when there is an exception during the S3 upload."""

    # Intercept the boto3 S3 client
    mock_s3_boto = mocker.patch('src.ntn_utils.boto3.client')

    # Mock the S3 put_object method to raise an exception
    mock_s3_boto.return_value.put_object.side_effect = Exception('S3 Upload Error')

    # Create a DataFrame with some data
    mock_df = pd.DataFrame([{'id': 'mock_id', 'title': 'mock_title'}])

    # Call the function and assert that it raises an exception
    with pytest.raises(Exception) as exc_info:
        ntn_utils.upload_to_s3(mock_df, 'mock_bucket_name', 'mock_file_name')

    # Assert the exception contains the expected message.
    assert "S3 Upload Error" == str(exc_info.value)


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            {
                'get_data_return_value': [{'id': 'mock_id', 'title': 'mock_title'}],
                'map_all_data_return_value': {'id': 'mock_id', 'title': 'mock_title'},
                'map_filtered_data_return_value': {'id': 'mock_id', 'title': 'mock_title'},
                'mock_event': {'run_id': '2026-07-05T15:36:00Z'},
                'expected_return': {'statusCode': 200, 'run_id': 20260705183600, 'body': 'mock_table extraction and load completed successfully!'},
                'expected_get_data_call_count': 2,
                'expected_upsert_stats_call_count': 3,
                'expected_upload_to_s3_call_count': 1,
            },
            id='New data is available for processing',
        ),
        pytest.param(
            {
                'get_data_return_value': [],
                'map_all_data_return_value': {},
                'map_filtered_data_return_value': {},
                'mock_event': {'run_id': '2026-07-05T15:36:00Z'},
                'expected_return': {'statusCode': 200, 'run_id': 20260705183600, 'body': 'mock_table extraction and load completed successfully!'},
                'expected_get_data_call_count': 2,
                'expected_upsert_stats_call_count': 3,
                'expected_upload_to_s3_call_count': 0,
            },
            id='No new data is available for processing',
        ),
        pytest.param(
            {
                'get_data_return_value': [],
                'map_all_data_return_value': {},
                'map_filtered_data_return_value': {},
                'mock_event': {},
                'expected_return': {'statusCode': 200, 'run_id': 99999999999999, 'body': 'mock_table extraction and load completed successfully!'},
                'expected_get_data_call_count': 2,
                'expected_upsert_stats_call_count': 3,
                'expected_upload_to_s3_call_count': 0,
            },
            id='The event is empty, simulating a full load scenario',
        ),
    ],
)
def test_run_full_extraction_pipeline(mocker,case):
    """
    Test the run_full_extraction_pipeline() function with various scenarios using parameterization.
    Scenario 1: New data is available for processing.
    Scenario 2: No new data is available for processing.
    Scenario 3: The event is empty, simulating a full load scenario.
    """

    mock_get_env = mocker.patch('src.ntn_utils.os.getenv')
    mock_engine = mocker.patch('src.ntn_utils.create_db_engine')
    mock_last_load_date = mocker.patch('src.ntn_utils.get_last_load_date')
    mock_get_data = mocker.patch('src.ntn_utils.get_data')
    mock_upsert_stats = mocker.patch('src.ntn_utils.upsert_into_stats')
    mock_upload_to_s3 = mocker.patch('src.ntn_utils.upload_to_s3')
    mock_load_new_data = mocker.patch('src.ntn_utils.load_new_data')
    mock_del_missing_data = mocker.patch('src.ntn_utils.del_missing_data')

    mock_map_all_data = mocker.MagicMock()
    mock_map_filtered_data = mocker.MagicMock()

    mock_get_data.return_value = case['get_data_return_value']
    mock_map_all_data.return_value = case['map_all_data_return_value']
    mock_map_filtered_data.return_value = case['map_filtered_data_return_value']

    event = case['mock_event']

    result = ntn_utils.run_full_extraction_pipeline(
        event,
        'mock_table',
        'mock_table_id',
        'mock_dag_name',
        'mock_task_name',
        mock_map_all_data,
        mock_map_filtered_data,
        'new_data_filter',
        'id_cols_filter',
    )

    assert result == case['expected_return']

    assert mock_get_data.call_count == case['expected_get_data_call_count']
    assert mock_upsert_stats.call_count == case['expected_upsert_stats_call_count']
    assert mock_upload_to_s3.call_count == case['expected_upload_to_s3_call_count']
