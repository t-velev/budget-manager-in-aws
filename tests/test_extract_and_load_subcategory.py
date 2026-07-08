import pendulum
import pytest
import src.extract_and_load_subcategory as extract_and_load_subcategory


@pytest.fixture
def mock_notion_json():

    json_item = {
        "object": "page",
        "id": "mock_id",
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2025-09-06T08:23:00.000Z",
        "created_by": {"object": "user", "id": "mock_id"},
        "last_edited_by": {"object": "user", "id": "mock_id"},
        "cover": "null",
        "icon": {"type": "emoji", "emoji": "🦷"},
        "parent": {"type": "database_id", "database_id": "mock_id"},
        "archived": False,
        "in_trash": False,
        "is_locked": False,
        "properties": {
            "Сума до целта": {"id": "mock_id", "type": "formula", "formula": {"type": "number", "number": 0}},
            "Скрий от Dashboard-а": {"id": "mock_id", "type": "checkbox", "checkbox": False},
            "Необходимост": {
                "id": "mock_id",
                "type": "select",
                "select": {"id": "mock_id", "name": "Плаваща", "color": "orange"},
            },
            "Приходи (трансфер)": {
                "id": "mock_id",
                "type": "rollup",
                "rollup": {"type": "number", "number": 0, "function": "sum"},
            },
            "Разходи": {
                "id": "mock_id",
                "type": "rollup",
                "rollup": {"type": "number", "number": 0, "function": "sum"},
            },
            "Година": {"id": "mock_id", "type": "relation", "relation": [{"id": "mock_id"}], "has_more": False},
            "Падеж": {
                "id": "mock_id",
                "type": "date",
                "date": {"start": "2022-03-08", "end": "null", "time_zone": "null"},
            },
            "Срок до целта": {"id": "mock_id", "type": "date", "date": "null"},
            "Общ бюджет": {"id": "mock_id", "type": "formula", "formula": {"type": "number", "number": 0}},
            "Тип": {"id": "mock_id", "type": "select", "select": {"id": "mock_id", "name": "Приход", "color": "green"}},
            "Сметка": {"id": "mock_id", "type": "relation", "relation": [{"id": "mock_id"}], "has_more": False},
            "Оставащо време": {"id": "mock_id", "type": "formula", "formula": {"type": "string", "string": "null"}},
            "Категория": {"id": "mock_id", "type": "relation", "relation": [{"id": "mock_id"}], "has_more": False},
            "Спестени": {"id": "mock_id", "type": "formula", "formula": {"type": "number", "number": 0}},
            "Бюджет": {"id": "mock_id", "type": "rollup", "rollup": {"type": "number", "number": 0, "function": "sum"}},
            "Общ Бюджет (не трий, скрий)": {
                "id": "mock_id",
                "type": "rollup",
                "rollup": {"type": "number", "number": 0, "function": "sum"},
            },
            "Бюджети v2 (не трий, скрий)": {"id": "mock_id", "type": "relation", "relation": [], "has_more": False},
            "Цел": {"id": "mock_id", "type": "number", "number": "null"},
            "Разходи (трансфер)": {
                "id": "mock_id",
                "type": "rollup",
                "rollup": {"type": "number", "number": 0, "function": "sum"},
            },
            "Похарчени за текущия": {"id": "mock_id", "type": "formula", "formula": {"type": "number", "number": 0}},
            "Статус": {"id": "mock_id", "type": "formula", "formula": {"type": "string", "string": "✅"}},
            "Related to Приходи и Разходи (Master DB) (Подкатегория)(НЕ ТРИЙ!)": {
                "id": "mock_id",
                "type": "relation",
                "relation": [],
                "has_more": False,
            },
            "Вноска": {"id": "mock_id", "type": "formula", "formula": {"type": "number", "number": "null"}},
            "Прогрес": {"id": "mock_id", "type": "formula", "formula": {"type": "number", "number": 0}},
            "Приходи": {
                "id": "mock_id",
                "type": "rollup",
                "rollup": {"type": "number", "number": 0, "function": "sum"},
            },
            "Архивирай": {"id": "mock_id", "type": "checkbox", "checkbox": True},
            "Име": {
                "id": "mock_id",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "За зъболекар", "link": "null"},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "plain_text": "За зъболекар",
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
    """Test that map_all_data returns the expected dictionary for the target raw database schema."""

    result = extract_and_load_subcategory.map_all_data(mock_notion_json)

    # Pull the load_date out of the result
    actual_load_date = result.pop("load_date")

    # Assert it separately, because there is always franctions differences
    # This checks if the generated date is within 5 seconds of right now
    assert (pendulum.now('UTC') - actual_load_date).in_seconds() < 5

    assert result == {
        'id': "mock_id",
        'title': "За зъболекар",
        'type': "Приход",
        'account_id': "mock_id",
        'category_id': "mock_id",
        'flex_type': "Плаваща",
        'due_date': "2022-03-08",
        "is_archived": True,
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2025-09-06T08:23:00.000Z"
    }


def test_map_filtered_data(mock_notion_json):
    """Test that map_filtered_data returns the expected dictionary for the notion_ids_audit table."""

    result = extract_and_load_subcategory.map_filtered_data(mock_notion_json)

    assert result == {
        "id": "mock_id",
        "title": "За зъболекар",
        "source_name": "subcategory"
    }


def test_subcategory_lambda_handler_wires_pipeline_correctly(mocker):
    """Test that lambda_handler calls the pipeline with the exact correct parameters."""
    
    # Intercept the pipeline function and mock its return value
    mock_pipeline = mocker.patch('src.extract_and_load_subcategory.run_full_extraction_pipeline')
    mock_pipeline.return_value = {'statusCode': 200, 'run_id': 1234, 'body': 'Success'}

    # Call the handler
    mock_event = {'run_id': '12345'}
    result = extract_and_load_subcategory.lambda_handler(mock_event, None)

    # Assert the lambda handler returns what the pipeline returned
    assert result == {'statusCode': 200, 'run_id': 1234, 'body': 'Success'}

    # Assert the exact right variables and functions were passed to the pipeline function
    mock_pipeline.assert_called_once_with(
        mock_event,
        'subcategory',                                                                # pg_table_name
        extract_and_load_subcategory.subcategory_db_id,                               # subcategory_db_id
        extract_and_load_subcategory.dag_name,                                        # dag_name
        extract_and_load_subcategory.task_name,                                       # task_name
        extract_and_load_subcategory.map_all_data,                                    # map_all_data (the function itself!)
        extract_and_load_subcategory.map_filtered_data,                               # map_filtered_data (the function itself!)
        ['Име', 'Тип', 'Сметка', 'Категория', 'Необходимост', 'Падеж', 'Архивирай'],  # new_data_filter
        ['Име']                                                                       # id_cols_filter
    )