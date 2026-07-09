import pytest
from sqlalchemy.exc import SQLAlchemyError
import src.reset_raw_notion_dates as reset_raw_notion_dates


def test_lambda_handler_success(mocker):
    """Test that the lambda_handler function executes successfully and resets the dates for all tables."""

    # Mock the event and context parameters
    mock_event = mocker.MagicMock()
    mock_context = mocker.MagicMock()

    # Mock the database engine and the connection inside the 'with' block
    mock_engine = mocker.patch('src.reset_raw_notion_dates.create_engine')
    mock_conn = mocker.MagicMock()

    # Teach the engine how to behave when 'with engine.begin() as conn:' is called
    mock_engine.return_value.begin.return_value.__enter__.return_value = mock_conn

    # Call the lambda_handler function
    result = reset_raw_notion_dates.lambda_handler(mock_event, mock_context)

    # Assert that the lambda_handler returns the expected success response
    assert result == {'statusCode': 200, 'body': 'Raw Notion dates reset completed successfully!'}

    # Assert that the execute method was called 7 times (once for each table)
    assert mock_conn.execute.call_count == 7

    # Check that the correct SQL queries were executed for each table
    all_calls = mock_conn.execute.call_args_list

    # Assert that the first table updated was 'account'
    first_call_args = mock_conn.execute.call_args_list[0][0][0]
    assert "update raw.account" in str(first_call_args)

    # Assert that the second table updated was 'category'
    second_call_args = mock_conn.execute.call_args_list[1][0][0]
    assert "update raw.category" in str(second_call_args)

    # Assert that the third table updated was 'subcategory'
    third_call_args = mock_conn.execute.call_args_list[2][0][0]
    assert "update raw.subcategory" in str(third_call_args)

    # Assert that the fourth table updated was 'year'
    fourth_call_args = mock_conn.execute.call_args_list[3][0][0]
    assert "update raw.year" in str(fourth_call_args)

    # Assert that the fifth table updated was 'month'
    fifth_call_args = mock_conn.execute.call_args_list[4][0][0]
    assert "update raw.month" in str(fifth_call_args)

    # Assert that the sixth table updated was 'budget'
    sixth_call_args = mock_conn.execute.call_args_list[5][0][0]
    assert "update raw.budget" in str(sixth_call_args)

    # Assert that the seventh table updated was 'transaction'
    seventh_call_args = mock_conn.execute.call_args_list[6][0][0]
    assert "update raw.transaction" in str(seventh_call_args)


def test_lambda_handler_exception(mocker):
    """Test that the lambda_handler function raises an SQLAlchemyError when the database update fails."""

    # Mock the event and context parameters
    mock_event = mocker.MagicMock()
    mock_context = mocker.MagicMock()

    # Mock the database engine and the connection inside the 'with' block
    mock_engine = mocker.patch('src.reset_raw_notion_dates.create_engine')
    mock_conn = mocker.MagicMock()

    # Teach the engine how to behave when 'with engine.begin() as conn:' is called
    mock_engine.return_value.begin.return_value.__enter__.return_value = mock_conn

    # Simulate an SQLAlchemyError when executing the first query
    mock_conn.execute.side_effect = SQLAlchemyError('DB Error')

    # Call the lambda_handler function and assert that it raises an SQLAlchemyError
    with pytest.raises(SQLAlchemyError) as exc_info:
        reset_raw_notion_dates.lambda_handler(mock_event, mock_context)

    # Assert the exception contains the expected message
    assert 'DB Error' == str(exc_info.value)
