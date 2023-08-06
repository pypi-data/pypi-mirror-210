import logging

from bovine.activitystreams.utils import actor_for_object

from bovine_process.types import ProcessingItem

logger = logging.getLogger(__name__)


async def accept_follow(item: ProcessingItem, actor) -> ProcessingItem:
    if item.data["type"] != "Accept":
        return item

    obj = item.data["object"]
    if isinstance(obj, str):
        obj = await actor.retrieve(obj)

    if obj["type"] != "Follow":
        return item

    remote_actor = actor_for_object(obj)

    await actor.add_to_followers(remote_actor)

    logger.info("Added %s to followers %s", remote_actor, actor.actor_object.followers)

    return item
