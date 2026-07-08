import pendulum
import pytest
import src.extract_and_load_budget as extract_and_load_budget


@pytest.fixture
def mock_notion_json():

    json_item = {
        "object": "page",
        "id": "mock_id_12345",
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2025-12-31T11:47:00.000Z",
        "created_by": {"object": "user", "id": "mock_id_12345"},
        "last_edited_by": {"object": "user", "id": "mock_id_12345"},
        "cover": "null",
        "icon": "null",
        "parent": {"type": "database_id", "database_id": "mock_id_12345"},
        "archived": False,
        "in_trash": False,
        "is_locked": False,
        "properties": {
            "Подкатегория": {
                "id": "mock_id_12345",
                "type": "relation",
                "relation": [{"id": "mock_id_12345"}],
                "has_more": False,
            },
            "Скрита": {"id": "mock_id_12345", "type": "checkbox", "checkbox": False},
            "Статус": {
                "id": "mock_id_12345",
                "type": "rollup",
                "rollup": {
                    "type": "array",
                    "array": [{"type": "formula", "formula": {"type": "string", "string": "✅"}}],
                    "function": "show_original",
                },
            },
            "Спестени": {
                "id": "mock_id_12345",
                "type": "rollup",
                "rollup": {"type": "number", "number": 0, "function": "sum"},
            },
            "Месец №": {
                "id": "mock_id_12345",
                "type": "rollup",
                "rollup": {"type": "number", "number": 6, "function": "sum"},
            },
            "Категория": {
                "id": "mock_id_12345",
                "type": "rollup",
                "rollup": {
                    "type": "array",
                    "array": [{"type": "relation", "relation": [{"id": "mock_id_12345"}]}],
                    "function": "show_original",
                },
            },
            "Месец": {
                "id": "mock_id_12345",
                "type": "relation",
                "relation": [{"id": "mock_id_12345"}],
                "has_more": False,
            },
            "Бюджет": {"id": "mock_id_12345", "type": "number", "number": "null"},
            "Тестов бюджет": {"id": "mock_id_12345", "type": "number", "number": "null"},
            "Бюджет BGN": {"id": "mock_id_12345", "type": "number", "number": 0},
            "Година": {
                "id": "mock_id_12345",
                "type": "relation",
                "relation": [{"id": "mock_id_12345"}],
                "has_more": False,
            },
            "Name": {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "РЕД", "link": "null"},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "plain_text": "РЕД",
                        "href": "null",
                    }
                ],
            },
            "Край период": {"id": "mock_id_12345", "type": "date", "date": {"start": "2026-06-30"}},
        },
        "url": "mock_url",
        "public_url": "null",
    }

    return json_item


def test_map_all_data(mock_notion_json):
    """Test that map_all_data returns the expected dictionary for the target raw database schema."""

    result = extract_and_load_budget.map_all_data(mock_notion_json)

    # Pull the load_date out of the result
    actual_load_date = result.pop("load_date")

    # Assert it separately, because there is always franctions differences
    # This checks if the generated date is within 5 seconds of right now
    assert (pendulum.now('UTC') - actual_load_date).in_seconds() < 5

    assert result == {
        'id':                'mock_id_12345',
        'title':             'РЕД',
        'period_end':        '2026-06-30',
        'budget_amount':     'null',
        'year_id':           'mock_id_12345',
        'month_id':          'mock_id_12345',
      # 'category_id':       ,
        'subcategory_id':    'mock_id_12345',
        'is_archived':       False,
        'created_time':      '2023-03-01T15:37:00.000Z',
        'last_edited_time':  '2025-12-31T11:47:00.000Z',
    }


def test_map_filtered_data(mock_notion_json):
    """Test that map_filtered_data returns the expected dictionary for the notion_ids_audit table."""

    result = extract_and_load_budget.map_filtered_data(mock_notion_json)

    assert result == {
        "id": "mock_id_12345",
        "title": "РЕД",
        "source_name": "budget"
    }


def test_budget_lambda_handler_wires_pipeline_correctly(mocker):
    """Test that lambda_handler calls the pipeline with the exact correct parameters."""
    
    # Intercept the pipeline function and mock its return value
    mock_pipeline = mocker.patch('src.extract_and_load_budget.run_full_extraction_pipeline')
    mock_pipeline.return_value = {'statusCode': 200, 'run_id': 1234, 'body': 'Success'}

    # Call the handler
    mock_event = {'run_id': '12345'}
    result = extract_and_load_budget.lambda_handler(mock_event, None)

    # Assert the lambda handler returns what the pipeline returned
    assert result == {'statusCode': 200, 'run_id': 1234, 'body': 'Success'}

    # Assert the exact right variables and functions were passed to the pipeline function
    mock_pipeline.assert_called_once_with(
        mock_event,
        'budget',                                                                        # pg_table_name
        extract_and_load_budget.budget_db_id,                                            # budget_db_id
        extract_and_load_budget.dag_name,                                                # dag_name
        extract_and_load_budget.task_name,                                               # task_name
        extract_and_load_budget.map_all_data,                                            # map_all_data (the function itself!)
        extract_and_load_budget.map_filtered_data,                                       # map_filtered_data (the function itself!)
        ['Name', 'Край период', 'Бюджет', 'Година', 'Месец', 'Подкатегория', 'Скрита'],  # new_data_filter
        ['Name']                                                                         # id_cols_filter
    )