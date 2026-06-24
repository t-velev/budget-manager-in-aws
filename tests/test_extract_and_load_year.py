import pendulum
import pytest
import src.extract_and_load_year as extract_and_load_year


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
            "Име": {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "2023", "link": "null"},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "plain_text": "2023",
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

    result = extract_and_load_year.map_all_data(mock_notion_json)

    # Pull the load_date out of the result
    actual_load_date = result.pop("load_date")

    # Assert it separately, because there is always franctions differences
    # This checks if the generated date is within 5 seconds of right now
    assert (pendulum.now('UTC') - actual_load_date).in_seconds() < 5

    assert result == {
        "id": "mock_id",
        "title": "2023",
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2023-03-01T15:37:00.000Z",
    }


def test_map_filtered_data(mock_notion_json):

    result = extract_and_load_year.map_filtered_data(mock_notion_json)

    assert result == {
        "id": "mock_id",
        "title": "2023",
        "source_name": "year"
    }
