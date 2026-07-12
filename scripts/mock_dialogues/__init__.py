from .cross_border_payments import build as build_cross_border_payments
from .distributed_cache import build as build_distributed_cache
from .notification_system import build as build_notification_system
from .typeahead_search import build as build_typeahead_search
from .object_storage import build as build_object_storage
from .fx_ledger import build as build_fx_ledger
from .top_k import build as build_top_k
from .chat_system import build as build_chat_system
from .location_service import build as build_location_service

BUILDERS = {
    "mock-cross-border-payments": build_cross_border_payments,
    "mock-distributed-cache": build_distributed_cache,
    "mock-notification-system": build_notification_system,
    "mock-typeahead-search": build_typeahead_search,
    "mock-object-storage": build_object_storage,
    "mock-fx-ledger": build_fx_ledger,
    "mock-top-k-heavy-hitters": build_top_k,
    "mock-chat-system": build_chat_system,
    "mock-location-service": build_location_service,
}
