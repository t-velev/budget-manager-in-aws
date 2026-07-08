import pendulum
import pytest
import src.extract_and_load_month as extract_and_load_month


@pytest.fixture
def mock_notion_json():

    json_item = {
        "object": "page",
        "id": "mock_id",
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2023-03-01T15:37:00.000Z",
        "created_by": {"object": "user", "id": "mock_id"},
        "last_edited_by": {"object": "user", "id": "mock_id"},
        "cover": "null",
        "icon": {"type": "emoji", "emoji": "🗓️"},
        "parent": {"type": "database_id", "database_id": "mock_id"},
        "archived": False,
        "in_trash": False,
        "is_locked": False,
        "properties": {
            "Общо разходи": {
                "id": "mock_id",
                "type": "rollup",
                "rollup": {"type": "number", "number": 714.2099999999999, "function": "sum"},
            },
            "🪙 Приходи и Разходи (Master DB) v2": {
                "id": "mock_id",
                "type": "relation",
                "relation": [
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                ],
                "has_more": True,
            },
            "Общо приходи": {
                "id": "mock_id",
                "type": "rollup",
                "rollup": {"type": "number", "number": 882.8, "function": "sum"},
            },
            "Подкатегории за годината": {
                "id": "mock_id",
                "type": "relation",
                "relation": [
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                ],
                "has_more": True,
            },
            "Месеци": {
                "id": "mock_id",
                "type": "relation",
                "relation": [
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                    {"id": "mock_id"},
                ],
                "has_more": False,
            },
            "Name": {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "January", "link": "null"},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "plain_text": "January",
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

    result = extract_and_load_month.map_all_data(mock_notion_json)

    # Pull the load_date out of the result
    actual_load_date = result.pop("load_date")

    # Assert it separately, because there is always franctions differences
    # This checks if the generated date is within 5 seconds of right now
    assert (pendulum.now('UTC') - actual_load_date).in_seconds() < 5

    assert result == {
        "id": "mock_id",
        "title": "January",
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2023-03-01T15:37:00.000Z",
    }


def test_map_filtered_data(mock_notion_json):

    result = extract_and_load_month.map_filtered_data(mock_notion_json)

    assert result == {
        "id": "mock_id",
        "title": "January",
        "source_name": "month"
    }


def test_month_lambda_handler_wires_pipeline_correctly(mocker):
    """Test that lambda_handler calls the pipeline with the exact correct parameters."""
    
    # Intercept the pipeline function and mock its return value
    mock_pipeline = mocker.patch('src.extract_and_load_month.run_full_extraction_pipeline')
    mock_pipeline.return_value = {'statusCode': 200, 'run_id': 1234, 'body': 'Success'}

    # Call the handler
    mock_event = {'run_id': '12345'}
    result = extract_and_load_month.lambda_handler(mock_event, None)

    # Assert the lambda handler returns what the pipeline returned
    assert result == {'statusCode': 200, 'run_id': 1234, 'body': 'Success'}

    # Assert the exact right variables and functions were passed to the pipeline function
    mock_pipeline.assert_called_once_with(
        mock_event,
        'month',                                     # pg_table_name
        extract_and_load_month.month_db_id,          # month_db_id
        extract_and_load_month.dag_name,             # dag_name
        extract_and_load_month.task_name,            # task_name
        extract_and_load_month.map_all_data,         # map_all_data (the function itself!)
        extract_and_load_month.map_filtered_data,    # map_filtered_data (the function itself!)
        ['Name'],                                    # new_data_filter
        ['Name']                                     # id_cols_filter
    )