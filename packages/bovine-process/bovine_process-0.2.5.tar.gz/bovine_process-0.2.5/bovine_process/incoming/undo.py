import json
import logging

from bovine_process.types import ProcessingItem

# from bovine.activitystreams.utils import actor_for_object


logger = logging.getLogger(__name__)


async def undo(item: ProcessingItem, actor) -> ProcessingItem:
    # owner = actor_for_object(data)

    object_to_undo = item.data.get("object")
    if isinstance(object_to_undo, dict):
        object_to_undo = object_to_undo.get("id")

    if object_to_undo is None:
        logger.warning("Undo without object %s", json.dumps(item.data))
        return

    # logger.info("Removing object with id %s for %s", object_to_undo, owner)

    # FIXME! What should an undo actually do?

    # await actor.remove(owner, object_to_undo)

    return
