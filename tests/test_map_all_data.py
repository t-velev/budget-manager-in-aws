import pendulum
import pytest
import src.extract_and_load_account as extract_and_load_account


def test_map_all_data():

    json_item = {
        "object": "page",
        "id": "mock_id_abcdef123456",
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

    result = extract_and_load_account.map_all_data(json_item)

    # Pull the load_date out of the result
    actual_load_date = result.pop("load_date")

    # Assert it separately, because there is always franctions differences
    # This checks if the generated date is within 5 seconds of right now
    assert (pendulum.now('UTC') - actual_load_date).in_seconds() < 5

    assert result == {
        "id": "mock_id_abcdef123456",
        "title": "Кеш",
        "is_archived": False,
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2023-03-01T15:37:00.000Z",
    }
