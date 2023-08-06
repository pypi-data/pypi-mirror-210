import logging

from bovine_process.types import ProcessingItem
from bovine_process.utils.update_id import update_id as update_id_function

logger = logging.getLogger(__name__)


async def update_id(item: ProcessingItem, actor) -> ProcessingItem:
    data = await update_id_function(item.data, actor)
    item.data = data

    item.meta["object_location"] = data["id"]

    return item
