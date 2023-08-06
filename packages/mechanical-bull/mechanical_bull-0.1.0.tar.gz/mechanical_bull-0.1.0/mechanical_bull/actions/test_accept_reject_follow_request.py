import pytest
from unittest.mock import AsyncMock, MagicMock

from bovine.activitystreams.activity_factory import Activity
from .accept_follow_request import handle as handle_accept
from .reject_follow_request import handle as handle_reject


@pytest.mark.parametrize("handle", [handle_accept, handle_reject])
async def test_does_nothing_on_random_activity(handle):
    data = {"type": "Note"}

    client = AsyncMock()

    await handle(client, data)

    client.send_to_outbox.assert_not_awaited()


@pytest.mark.parametrize("handle", [handle_accept, handle_reject])
async def test_replies_to_follow_with_accept(handle):
    data = Activity(id="uuid", type="Follow", actor="actor").build()
    client = AsyncMock()
    client.activity_factory.accept = MagicMock()

    await handle(client, data)

    client.send_to_outbox.assert_awaited_once()
