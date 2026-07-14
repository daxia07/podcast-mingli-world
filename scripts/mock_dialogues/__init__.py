from .cross_border_payments import build as build_cross_border_payments
from .distributed_cache import build as build_distributed_cache
from .notification_system import build as build_notification_system
from .typeahead_search import build as build_typeahead_search
from .object_storage import build as build_object_storage
from .fx_ledger import build as build_fx_ledger
from .top_k import build as build_top_k
from .chat_system import build as build_chat_system
from .location_service import build as build_location_service
from .web_crawler import build as build_web_crawler
from .key_value_store import build as build_key_value_store
from .rate_limiter import build as build_rate_limiter
from .video_streaming import build as build_video_streaming
from .ride_sharing import build as build_ride_sharing
from .distributed_wallet import build as build_distributed_wallet
from .ai_agent_platform import build as build_ai_agent_platform
from .security_automation import build as build_security_automation
from .job_scheduler import build as build_job_scheduler
from .metrics_pipeline import build as build_metrics_pipeline
from .global_treasury import build as build_global_treasury
from .feature_store import build as build_feature_store
from .fraud_detection import build as build_fraud_detection

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
    "mock-web-crawler": build_web_crawler,
    "mock-key-value-store": build_key_value_store,
    "mock-rate-limiter": build_rate_limiter,
    "mock-video-streaming": build_video_streaming,
    "mock-ride-sharing": build_ride_sharing,
    "mock-distributed-wallet": build_distributed_wallet,
    "mock-ai-agent-platform": build_ai_agent_platform,
    "mock-security-automation": build_security_automation,
    "mock-job-scheduler": build_job_scheduler,
    "mock-metrics-pipeline": build_metrics_pipeline,
    "mock-global-treasury": build_global_treasury,
    "mock-feature-store": build_feature_store,
    "mock-fraud-detection": build_fraud_detection,
}
