import uuid
from unittest.mock import AsyncMock

from quart import Quart

from .update_id import update_id

app = Quart(__name__)


async def test_update_id():
    actor = AsyncMock()
    actor.generate_new_object_id = lambda: str(uuid.uuid4())

    data = {"id": "id"}
    result = await update_id(data, actor)
    assert result["id"] != "id"

    data = {"object": "test"}
    result = await update_id(data, actor)
    assert result["id"]

    # if in store; id is not updated
    data = {"object": {"id": "id"}}
    result = await update_id(data, actor)
    assert result["object"]["id"] == "id"

    actor.retrieve.return_value = None
    data = {"object": {"id": "id"}}
    result = await update_id(data, actor)
    assert result["object"]["id"] != "id"
