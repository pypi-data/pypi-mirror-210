from unittest.mock import patch, AsyncMock

from .event_loop import handle_connection


@patch("bovine.BovineClient")
async def test_loop_no_loop(mock_client):
    mock_client.return_value = mock_client

    source = AsyncMock()
    mock_client.__aenter__ = AsyncMock()
    mock_client.__aenter__.return_value = mock_client

    mock_client.event_source = AsyncMock()
    mock_client.event_source.return_value = source
    source.sequence = []

    await handle_connection(mock_client, [])

    mock_client.event_source.assert_awaited_once()
