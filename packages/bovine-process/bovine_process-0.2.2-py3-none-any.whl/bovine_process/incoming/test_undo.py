from unittest.mock import MagicMock

import pytest
from bovine_store.utils.test import store  # noqa F401

from bovine_process.types import ProcessingItem

from .store_incoming import store_incoming
from .undo import undo


async def test_undo_bad_format(store):  # noqa F801
    first_id = "https://my_domain/first"
    item = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": first_id,
        "type": "Undo",
    }

    processing_item = ProcessingItem("tag:actor", item)

    result = await undo(processing_item, {})

    assert result is None


@pytest.mark.skip("FIXME: Not sure what to implement")
async def test_undo(store):  # noqa F801a
    actor = "https://remote_actor"
    first_id = "https://my_domain/first"
    second_id = "https://my_domain/second"

    item = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Like",
        "actor": actor,
        "id": second_id,
    }

    processing_item = ProcessingItem(actor, item)

    result = await store_incoming(
        processing_item, store, MagicMock(actor_id="local_user_id")
    )

    undo_item = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": first_id,
        "actor": actor,
        "type": "Undo",
        "object": item,
    }

    processing_item = ProcessingItem(actor, undo_item)
    result = await undo(processing_item, store, {})

    assert result is None

    first = await store.retrieve("local_actor_url", first_id)
    second = await store.retrieve("local_actor_url", second_id)

    assert first is None
    assert second is None
