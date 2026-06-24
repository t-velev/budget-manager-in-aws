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

    result = extract_and_load_budget.map_filtered_data(mock_notion_json)

    assert result == {
        "id": "mock_id_12345",
        "title": "РЕД",
        "source_name": "budget"
    }
