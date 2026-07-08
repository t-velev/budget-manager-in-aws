import pendulum
import pytest
import src.extract_and_load_account as extract_and_load_account


@pytest.fixture
def mock_notion_json():

    json_item = {
        "object": "page",
        "id": "mock_id",
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2023-03-01T15:37:00.000Z",
        "created_by": {"object": "user", "id": "mock_id_abcdef"},
        "last_edited_by": {"object": "user", "id": "mock_id_abcdef"},
        "cover": "null",
        "icon": {"type": "emoji", "emoji": "💵"},
        "parent": {"type": "database_id", "database_id": "mock_db_id_abcdef"},
        "archived": False,
        "in_trash": False,
        "is_locked": False,
        "properties": {
            "Архивирай": {"id": "NiYw", "type": "checkbox", "checkbox": False},
            "Name": {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "Кеш", "link": "null"},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "plain_text": "Кеш",
                        "href": "null",
                    }
                ],
            },
        },
        "url": "mock_url",
        "public_url": "null",
    }

    return json_item


def test_map_all_data(mock_notion_json):

    result = extract_and_load_account.map_all_data(mock_notion_json)

    # Pull the load_date out of the result
    actual_load_date = result.pop("load_date")

    # Assert it separately, because there is always franctions differences
    # This checks if the generated date is within 5 seconds of right now
    assert (pendulum.now('UTC') - actual_load_date).in_seconds() < 5

    assert result == {
        "id": "mock_id",
        "title": "Кеш",
        "is_archived": False,
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2023-03-01T15:37:00.000Z",
    }


def test_map_filtered_data(mock_notion_json):

    result = extract_and_load_account.map_filtered_data(mock_notion_json)

    assert result == {
        "id": "mock_id",
        "title": "Кеш",
        "source_name": "account"
    }


def test_account_lambda_handler_wires_pipeline_correctly(mocker):
    """Test that lambda_handler calls the pipeline with the exact correct parameters."""
    
    # Intercept the pipeline function and mock its return value
    mock_pipeline = mocker.patch('src.extract_and_load_account.run_full_extraction_pipeline')
    mock_pipeline.return_value = {'statusCode': 200, 'run_id': 1234, 'body': 'Success'}

    # Call the handler
    mock_event = {'run_id': '12345'}
    result = extract_and_load_account.lambda_handler(mock_event, None)

    # Assert the lambda handler returns what the pipeline returned
    assert result == {'statusCode': 200, 'run_id': 1234, 'body': 'Success'}

    # Assert the exact right variables and functions were passed to the pipeline function
    mock_pipeline.assert_called_once_with(
        mock_event,
        'account',                                   # pg_table_name
        extract_and_load_account.account_db_id,      # account_db_id
        extract_and_load_account.dag_name,           # dag_name
        extract_and_load_account.task_name,          # task_name
        extract_and_load_account.map_all_data,       # map_all_data (the function itself!)
        extract_and_load_account.map_filtered_data,  # map_filtered_data (the function itself!)
        ['Name', 'Архивирай'],                       # new_data_filter
        ['Name']                                     # id_cols_filter
    )