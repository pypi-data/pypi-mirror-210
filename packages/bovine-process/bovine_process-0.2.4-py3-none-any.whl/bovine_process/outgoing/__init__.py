from bovine_process.add_to_queue import add_to_queue
from bovine_process.utils.processor_list import ProcessorList

from .accept_follow import accept_follow
from .outgoing_delete import outgoing_delete
from .outgoing_update import outgoing_update
from .store_outgoing import add_outgoing_to_outbox, store_outgoing
from .update_id import update_id

default_outbox_process = (
    ProcessorList()
    .add(update_id)
    .add(store_outgoing)
    .add(add_outgoing_to_outbox)
    .add_for_types(
        Update=outgoing_update,
        Delete=outgoing_delete,
    )
    .apply
)


default_async_outbox_process = (
    ProcessorList().add_for_types(Accept=accept_follow).add(add_to_queue).apply
)
