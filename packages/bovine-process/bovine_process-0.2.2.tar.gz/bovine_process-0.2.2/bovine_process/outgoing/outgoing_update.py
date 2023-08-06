import logging

from bovine_process.types import ProcessingItem

logger = logging.getLogger(__name__)


async def outgoing_update(item: ProcessingItem, actor) -> ProcessingItem:
    object_to_update = item.data.get("object")
    object_to_update["@context"] = item.data["@context"]
    if object_to_update is None or object_to_update.get("id") is None:
        logger.warning("Update without object %s", item.body)
        return

    to_update_from_db = await actor.retrieve(
        object_to_update.get("id"), skip_fetch=True
    )

    if to_update_from_db["attributedTo"] != actor.actor_id:
        logger.warning(
            "Update from different actor %s in %s for object with id %s",
            actor.actor_id,
            item.data.get("id"),
            object_to_update.get("id"),
        )
        return

    # FIXME: More sanity checks?

    if to_update_from_db:
        await actor.update(object_to_update)

    return item
