import pendulum
import pytest
import src.extract_and_load_transaction as extract_and_load_transaction


@pytest.fixture
def mock_notion_json():

    json_item = {
        "object": "page",
        "id": "mock_id",
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2025-12-31T10:53:00.000Z",
        "created_by": {"object": "user", "id": "mock_id"},
        "last_edited_by": {"object": "user", "id": "mock_id"},
        "cover": "null",
        "icon": "null",
        "parent": {"type": "database_id", "database_id": "mock_id"},
        "in_trash": False,
        "is_archived": False,
        "is_locked": False,
        "properties": {
            "Name": {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "TickTick", "link": "null"},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "plain_text": "TickTick",
                        "href": "null",
                    }
                ],
            },
            "Тип": {"id": "xg%3Ej", "type": "select", "select": {"id": "gCEN", "name": "Разход", "color": "red"}},
            "Дата": {
                "id": "dpP%5E",
                "type": "date",
                "date": {"start": "2022-03-21", "end": "null", "time_zone": "null"},
            },
            "Сума": {"id": "%3AepJ", "type": "number", "number": 2.56},
            "Статус": {"id": "LVx%5C", "type": "select", "select": {"id": "@kG@", "name": "Платено", "color": "green"}},
            "Бележка": {"id": "LsU%5E", "type": "rich_text", "rich_text": []},
            "Година": {"id": "%60Kvx", "type": "relation", "relation": [{"id": "mock_id"}], "has_more": False},
            "Месец": {"id": "t%5Dsm", "type": "relation", "relation": [{"id": "mock_id"}], "has_more": False},
            "Подкатегория": {"id": "U_%3FP", "type": "relation", "relation": [{"id": "mock_id"}], "has_more": False},
            "Template": {"id": "Nrf%40", "type": "checkbox", "checkbox": False},
        },
        "url": "mock_url",
        "public_url": "null",
        "archived": False,
    }

    return json_item


def test_map_all_data(mock_notion_json):

    result = extract_and_load_transaction.map_all_data(mock_notion_json)

    # Pull the load_date out of the result
    actual_load_date = result.pop("load_date")

    # Assert it separately, because there is always franctions differences
    # This checks if the generated date is within 5 seconds of right now
    assert (pendulum.now('UTC') - actual_load_date).in_seconds() < 5

    assert result == {
        'id': "mock_id",
        'title': "TickTick",
        'type': "Разход",
        'date': "2022-03-21",
        'amount': 2.56,
        'status': "Платено",
        'note': None,
        'year_id': "mock_id",
        'month_id': "mock_id",
      # 'category_id': "mock_id",
        'subcategory_id': "mock_id",
      # 'account_id': "mock_id",
        'is_template': False,
        'created_time': "2023-03-01T15:37:00.000Z",
        'last_edited_time': "2025-12-31T10:53:00.000Z"
    }


def test_map_filtered_data(mock_notion_json):

    result = extract_and_load_transaction.map_filtered_data(mock_notion_json)

    assert result == {
        "id": "mock_id",
        "title": "TickTick",
        "source_name": "transaction"
    }
