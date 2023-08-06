import logging

from bovine.activitystreams.utils import actor_for_object

from bovine_process.types import ProcessingItem

logger = logging.getLogger(__name__)


async def follow_accept(item: ProcessingItem, actor) -> ProcessingItem:
    if item.data["type"] != "Accept":
        return item

    obj = item.data["object"]
    if isinstance(obj, str):
        logger.info("retrieving remote object %s for %s", obj, actor.actor_id)
        obj = await actor.retrieve(obj)

    if obj["type"] != "Follow":
        return item

    if obj["actor"] != actor.actor_id:
        logger.warning("Got following for incorrect actor %s", obj["actor"])
        return item

    remote_actor = actor_for_object(item.data)
    await actor.add_to_following(remote_actor)

    logger.info("Added %s to following %s", remote_actor, actor.actor_object.following)

    return item
