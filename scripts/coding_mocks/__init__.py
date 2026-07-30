"""Two-voice coding mock interviews and drills for Airwallex Stage 1."""

from .rate_limiter import build as build_rate_limiter
from .currency_best_rate import build as build_currency_best_rate
from .refund_rules import build as build_refund_rules
from .stream_topk import build as build_stream_topk
from .ai_deep_dive_part2 import build as build_ai_deep_dive_part2
from .stuck_recovery import build as build_stuck_recovery
from .clarify_gym import build as build_clarify_gym
from .intro_drills import build as build_intro_drills
from .wrong_answers_clinic import build as build_wrong_answers_clinic
from .lru_cache import build as build_lru_cache
from .rpn_evaluator import build as build_rpn_evaluator
from .idempotency_store import build as build_idempotency_store
from .complexity_edges_drill import build as build_complexity_edges_drill
from .full_hour_dual_mode import build as build_full_hour_dual_mode
from .mono_stack_temperatures import build as build_mono_stack
from .fx_anomaly import build as build_fx_anomaly
from .bellman_ford_arbitrage import build as build_bellman_ford
from .two_sum import build as build_two_sum
from .longest_substring import build as build_longest_substring
from .container_water import build as build_container_water
from .merge_intervals import build as build_merge_intervals
from .num_islands import build as build_num_islands
from .coin_change import build as build_coin_change

BUILDERS = {
    "coding-mock-rate-limiter": build_rate_limiter,
    "coding-mock-currency-best-rate": build_currency_best_rate,
    "coding-mock-refund-rules": build_refund_rules,
    "coding-mock-stream-topk": build_stream_topk,
    "coding-mock-full-hour-dual-mode": build_full_hour_dual_mode,
    "coding-mock-ai-deep-dive-part2": build_ai_deep_dive_part2,
    "coding-mock-stuck-recovery": build_stuck_recovery,
    "coding-mock-clarify-gym": build_clarify_gym,
    "coding-mock-intro-drills": build_intro_drills,
    "coding-mock-wrong-answers": build_wrong_answers_clinic,
    "coding-mock-lru-cache": build_lru_cache,
    "coding-mock-rpn": build_rpn_evaluator,
    "coding-mock-idempotency": build_idempotency_store,
    "coding-mock-complexity-edges": build_complexity_edges_drill,
    "coding-mock-mono-stack": build_mono_stack,
    "coding-mock-fx-anomaly": build_fx_anomaly,
    "coding-mock-bellman-ford": build_bellman_ford,
    "coding-mock-two-sum": build_two_sum,
    "coding-mock-longest-substring": build_longest_substring,
    "coding-mock-container-water": build_container_water,
    "coding-mock-merge-intervals": build_merge_intervals,
    "coding-mock-num-islands": build_num_islands,
    "coding-mock-coin-change": build_coin_change,
}
