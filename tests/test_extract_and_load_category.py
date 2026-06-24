import pendulum
import pytest
import src.extract_and_load_category as extract_and_load_category


@pytest.fixture
def mock_notion_json():

    json_item = {
        "object": "page",
        "id": "mock_id_abcdef123456",
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2023-03-01T15:37:00.000Z",
        "created_by": {"object": "user", "id": "mock_id_abcdef"},
        "last_edited_by": {"object": "user", "id": "mock_id_abcdef"},
        "cover": "null",
        "icon": {"type": "emoji", "emoji": "🏄"},
        "parent": {"type": "database_id", "database_id": "mock_db_id_abcdef"},
        "archived": False,
        "in_trash": False,
        "is_locked": False,
        "properties": {
            "Архивирай": {"id": "NiYw", "type": "checkbox", "checkbox": False},
            "Тип": {
                "id": "uqgT",
                "type": "select",
                "select": {"id": "mock_id_abcdef", "name": "Разход", "color": "red"},
            },
            "Name": {
                "id": "title",
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "11: Почивка/отпуска", "link": "null"},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "plain_text": "11: Почивка/отпуска",
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

    result = extract_and_load_category.map_all_data(mock_notion_json)

    # Pull the load_date out of the result
    actual_load_date = result.pop("load_date")

    # Assert it separately, because there is always franctions differences
    # This checks if the generated date is within 5 seconds of right now
    assert (pendulum.now('UTC') - actual_load_date).in_seconds() < 5

    assert result == {
        "id": "mock_id_abcdef123456",
        "title": "11: Почивка/отпуска",
        "type": "Разход",
        "is_archived": False,
        "created_time": "2023-03-01T15:37:00.000Z",
        "last_edited_time": "2023-03-01T15:37:00.000Z",
    }


def test_map_filtered_data(mock_notion_json):

    result = extract_and_load_category.map_filtered_data(mock_notion_json)

    assert result == {
        "id": "mock_id_abcdef123456",
        "title": "11: Почивка/отпуска",
        "source_name": "category"
    }
