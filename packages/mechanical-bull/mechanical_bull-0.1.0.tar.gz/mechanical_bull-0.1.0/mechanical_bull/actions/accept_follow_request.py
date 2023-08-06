import logging

from bovine import BovineActor

logger = logging.getLogger(__name__)


async def handle(actor: BovineActor, data: dict):
    if data["type"] != "Follow":
        return

    follow_actor = data["actor"]
    if isinstance(follow_actor, dict):
        follow_actor = follow_actor["id"]

    logger.info("Accepting follow request from %s", follow_actor)

    accept = actor.activity_factory.accept(data["id"], to={data["actor"]}).build()

    await actor.send_to_outbox(accept)
