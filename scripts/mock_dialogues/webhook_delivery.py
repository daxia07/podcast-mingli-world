"""Mock Interview: Reliable Webhook & Event Delivery Platform — Two-voice dialogue."""


def build():
    lines = []

    # SECTION 1: Requirements
    lines.append(("interviewer", "Hi, welcome. Today I'd like you to design a webhook platform for a payments company. Merchants need near-real-time notifications when payments change status. The platform must deliver millions of events per day to arbitrary customer endpoints. It must support endpoint configuration, signatures, retries, replay, tenant isolation, observability, and recovery when the customer endpoint is slow or unavailable. Webhook delivery must never block payment processing."))

    lines.append(("candidate", "Thanks. Webhook delivery is a deceptively hard problem — it sounds simple, just POST to a URL, but the moment you have millions of events, slow endpoints, and security concerns, it becomes a distributed systems challenge. The key insight is the outbox pattern: payment state transitions write immutable events to an outbox in the same database transaction, and an independent event service fans them out to subscribed endpoints. Let me clarify the requirements. First, what's the delivery guarantee — at-least-once or exactly-once?"))

    lines.append(("interviewer", "At-least-once. We tell merchants to deduplicate by event ID. Exactly-once delivery over HTTP is impossible — the receiver could process the message and crash before sending the acknowledgment, and on retry we'd deliver it again."))

    lines.append(("candidate", "Second question: what's the delivery latency target, and is there an ordering guarantee?"))

    lines.append(("interviewer", "Latency target: deliver within five seconds of the state change for ninety-nine percent of events. No global ordering guarantee — events for different payments can arrive in any order. But for a specific payment, merchants would prefer events arrive in order — payment.created before payment.settled."))

    lines.append(("candidate", "Third question: what security measures are needed? How do we prevent SSRF — Server-Side Request Forgery — where a merchant configures a webhook URL that points to an internal service?"))

    lines.append(("interviewer", "Good question. We need to validate endpoint URLs against private IP ranges, block redirects to internal IPs, and use egress controls. Merchants must verify endpoint ownership — we send a challenge and they must respond. Signature rotation is also required — merchants can rotate their webhook secret without downtime."))

    lines.append(("candidate", "Summary: at-least-once delivery with merchant-side deduplication, five-second p99 latency, per-resource ordering preferred but not globally guaranteed, endpoint verification, SSRF protection, signature rotation, tenant isolation, and delivery must never block payment processing. Moving to architecture."))

    # SECTION 2: Architecture
    lines.append(("interviewer", "Show me the architecture."))

    lines.append(("candidate", "The architecture has three layers. Layer one: event creation. When a payment state transition commits — say, payment moves from submitted to settled — the payment service writes the new payment state and an outbox event in the same database transaction. The outbox event is immutable — event ID, event type, payload, tenant ID, and creation timestamp. This is the transactional outbox pattern, and it guarantees that every state change produces an event, and no event is created without a corresponding state change."))

    lines.append(("candidate", "Layer two: event fan-out. An outbox publisher — either a polling process or a CDC stream like Debezium — reads new outbox events and publishes them to the event store. The event store is the permanent, immutable record of all events. It's independent from delivery attempts. Then, a subscription matcher looks up all active webhook endpoints subscribed to this event type for this tenant. For each matching endpoint, it creates a delivery record — endpoint ID, event ID, status pending, next attempt time, attempt count zero. The delivery record is the unit of work for the delivery workers."))

    lines.append(("candidate", "Layer three: delivery. Workers pick up pending delivery records, resolve the endpoint URL, apply SSRF checks, construct the signed payload, and POST it to the merchant's endpoint. On a 2xx response, the delivery is marked as delivered. On a transient error — network timeout, 5xx from the merchant's server, 429 rate limit — the worker marks the attempt, calculates the next retry time with exponential backoff and jitter, and moves on. On a permanent error — 4xx client error, not 429 — the worker marks the attempt and either retries with lower priority or marks as permanently failed, depending on the error code. Each endpoint has its own concurrency and rate budget, so a slow or failing merchant endpoint cannot impact delivery to other merchants."))

    # SECTION 3: Deep Dive — Delivery Contract
    lines.append(("interviewer", "Show me the webhook payload and signature."))

    lines.append(("candidate", "The webhook POST includes several headers and a JSON body. Headers: X-Event-ID with a stable unique identifier like evt underscore one two three. X-Event-Type like payment dot settled. X-Webhook-Timestamp — the Unix timestamp of the delivery attempt. X-Webhook-Signature — an HMAC SHA-256 of the timestamp concatenated with a period and the request body, using the merchant's webhook secret. And Content-Type application/json. The body includes the event ID, type, the full event data — payment ID, amount, currency, status, timestamps — and an API version field so merchants can handle schema evolution."))

    lines.append(("candidate", "The signature serves two purposes: authenticity — only someone with the secret could generate it — and integrity — any change to the body invalidates it. Merchants verify by recomputing the HMAC and comparing. During secret rotation, we support two secrets simultaneously — the current and the previous — for a grace period. The signature header includes a version prefix like v1 equals HMAC value, so we can add new signature algorithms later without breaking existing verification."))

    lines.append(("interviewer", "What's the retry policy?"))

    lines.append(("candidate", "Exponential backoff with jitter, starting at one minute and increasing to one hour over about ten attempts. Total retry window: seventy-two hours. After that, the delivery is marked as permanently failed and surfaced in the merchant's dashboard. The jitter — a random delay added to each backoff interval — prevents thundering herd effects where thousands of endpoints all retry simultaneously after a platform-wide incident."))

    lines.append(("candidate", "Critically, each endpoint has its own retry schedule. If merchant A's endpoint is down, their retries happen independently of merchant B's. The delivery records are partitioned by endpoint ID, and each partition has its own worker pool. This is tenant isolation at the infrastructure level — no shared queue where one bad endpoint creates head-of-line blocking for everyone."))

    # SECTION 4: Deep Dive — SSRF and Security
    lines.append(("interviewer", "Walk me through the SSRF protection in detail."))

    lines.append(("candidate", "SSRF — Server-Side Request Forgery — is a critical security concern for webhook platforms. A malicious merchant could configure a webhook URL pointing to an internal service — like http://metadata.google.internal to steal cloud credentials, or http://localhost:6379 to interact with an internal Redis. Our defense has four layers. Layer one: URL validation at configuration time. We parse the URL, reject private IP ranges — ten dot, one seven two dot, one nine two dot one six eight, localhost, and link-local addresses. We reject non-HTTP protocols — no file://, no gopher://. We reject URLs with credentials embedded — user:password@host."))

    lines.append(("candidate", "Layer two: DNS rebinding protection at delivery time. Between configuration and delivery, the domain could have been re-pointed to a private IP. Before each delivery attempt, we re-resolve the domain and validate the resolved IP against the same private-range block. We cache the resolved IP for a short period — maybe five minutes — to prevent a time-of-check-time-of-use attack where DNS changes between resolution and connection."))

    lines.append(("candidate", "Layer three: redirect restrictions. We limit HTTP redirects to two hops, and each redirect target is validated with the same URL and IP checks. An attacker could configure a legitimate URL that redirects to an internal service. Layer four: egress network controls. At the infrastructure level, we use firewall rules or egress proxies that block connections to private IP ranges entirely. Even if an application-level check is bypassed, the network-level control prevents the connection. Defense in depth — never rely on a single layer for security."))

    # SECTION 5: Failure and Recovery
    lines.append(("interviewer", "What happens when the event bus or the delivery workers have an outage?"))

    lines.append(("candidate", "Because we use the transactional outbox pattern, the event is safely stored in the payment database alongside the state change. If the event bus goes down, no events are lost — they accumulate in the outbox table. When the event bus recovers, the outbox publisher catches up by scanning for unprocessed events. Payment processing is completely unaffected — it doesn't wait for event delivery. This is the fundamental guarantee: webhook delivery never blocks payment processing."))

    lines.append(("candidate", "If delivery workers have an outage, delivery records accumulate in pending state. When workers recover, they process the backlog using normal retry schedules. Events that were created during the outage are delivered late, but they're not lost. Merchants who need to catch up can also use the event-list API — a REST endpoint that returns events by ID range, time range, or event type. This is the recovery path for merchants who missed events during a prolonged outage or whose own systems had a bug."))

    lines.append(("interviewer", "How does event replay work? A merchant says they lost events due to a bug on their side."))

    lines.append(("candidate", "The merchant can request a replay through the dashboard or API. They specify a time range or event ID range. Replay creates new delivery records — new attempt records for the same immutable events. It does not create new financial events. The merchant receives the events again with the same event IDs, so their deduplication logic handles them correctly. Replay is rate-limited to prevent abuse — a merchant can request one replay per hour, and the replay delivers at a controlled rate to avoid overwhelming their endpoint."))

    # SECTION 6: Ordering and Scale
    lines.append(("interviewer", "You mentioned per-resource ordering. How do you implement that?"))

    lines.append(("candidate", "Per-resource ordering means that for a specific payment ID, events are delivered in the order they were created — payment.created, then payment.authenticated, then payment.settled. We achieve this by sharding delivery by endpoint ID plus resource ID. Events for the same endpoint and the same payment go to the same delivery worker partition, which processes them in order. Events for different payments on the same endpoint can be processed in parallel. This gives per-resource ordering without sacrificing overall throughput."))

    lines.append(("candidate", "But there's a trade-off: ordering reduces parallelism. If a merchant has one slow payment event, it doesn't block events for other payments, but it does block subsequent events for that specific payment. If the merchant's endpoint is slow, ordered delivery makes the latency worse for that resource. That's why ordering is optional — merchants can opt into it, and the default is unordered delivery for maximum throughput. Most merchants don't need strict ordering — they can handle out-of-order events by looking at the event timestamp or the payment state."))

    lines.append(("interviewer", "How do you handle high retry volume — say, a cloud provider outage affects many merchant endpoints simultaneously?"))

    lines.append(("candidate", "This is the thundering herd scenario. When a major cloud provider goes down, thousands of merchant endpoints become unreachable simultaneously, and all their retries start accumulating. Our defense: backoff with jitter, endpoint rate budgets, retry queue age alarms, and automatic endpoint disablement. The jitter randomizes retry times, spreading the load. Endpoint rate budgets cap the number of delivery attempts per minute for each endpoint, preventing our workers from being overwhelmed. Retry queue age alarms trigger when the average age of pending deliveries exceeds a threshold — this tells us something systemic is wrong. And automatic endpoint disablement: if an endpoint fails persistently for twenty-four hours, we mark it as disabled and notify the merchant. We stop retrying, which frees up worker capacity for healthy endpoints. The merchant can re-enable it when their system is fixed."))

    # SECTION 7: Summary with Killer Phrases
    lines.append(("candidate", "Let me close with the killer phrases for webhook delivery. One: transactional outbox — events are written in the same transaction as the state change, so delivery never blocks processing and no event is lost. Two: at-least-once with merchant deduplication — exactly-once over HTTP is impossible, so receivers must deduplicate by event ID. Three: per-endpoint queues and rate budgets — a failing endpoint must not create head-of-line blocking for other merchants. Four: re-resolve DNS at delivery time — DNS rebinding is a real SSRF vector, validate the resolved IP before connecting. Five: exponential backoff with jitter prevents thundering herds — randomize retry times to spread load after platform incidents. Six: replay creates new delivery attempts, not new financial events — the same event ID is reused so merchant deduplication handles it. Seven: signature rotation supports two secrets during grace period — v1 equals HMAC with current, v1 equals HMAC with previous. Eight: webhook push for latency, event-list API for recovery and audit — merchants need both push and pull. The phrase to remember: transactional outbox, delivery never blocks processing."))

    lines.append(("interviewer", "Walk me through the complete flow for a payment status change webhook."))

    lines.append(("candidate", "Step one: payment settles. The payment service updates the payment state from submitted to settled. In the same database transaction, it writes an outbox event: event ID evt-789, type payment.settled, payload with payment ID, amount, currency, settlement timestamp, and tenant ID. The transaction commits. The payment is settled, and the event exists — atomically."))

    lines.append(("candidate", "Step two: outbox publisher picks up the new event within one second — it polls or receives a CDC notification. It publishes the event to the event store, which is the permanent immutable record. It marks the outbox row as published."))

    lines.append(("candidate", "Step three: subscription matcher finds two endpoints for this tenant that subscribe to payment.settled. Endpoint one: https://api.merchant.example/webhooks with a concurrency budget of ten and a rate budget of one hundred per minute. Endpoint two: https://erp.merchant.example/notifications with a concurrency budget of three and a rate budget of twenty per minute. The matcher creates two delivery records, one for each endpoint, both in pending state."))

    lines.append(("candidate", "Step four: delivery worker picks up the delivery record for endpoint one. It re-resolves api.merchant.example — the IP is fifty-two dot thirty-one dot one two three dot forty-five, which is a public AWS IP. SSRF check passes. It constructs the payload with all the required headers, computes the HMAC signature using the merchant's current secret, and sends the POST. The merchant responds with 200 OK within two hundred milliseconds. Delivery marked as delivered. Total time from payment settlement to merchant notification: about three seconds."))

    lines.append(("candidate", "Step five: delivery worker picks up the delivery record for endpoint two. It resolves erp.merchant.example, sends the POST, but gets a 503 Service Unavailable after a five-second timeout. The worker marks the attempt, calculates the next retry time — one minute plus a random jitter of zero to thirty seconds — and moves on. The delivery record stays in pending state with next-attempt time set. A minute later, the worker retries and gets a 200 OK. Delivered."))

    lines.append(("candidate", "If endpoint two had been down for hours, the retries would continue with exponential backoff — one minute, two minutes, four minutes, up to one hour intervals — for up to seventy-two hours. If it never recovers, the delivery is marked as permanently failed, and the merchant sees it in their dashboard. They can use the event-list API to fetch the missed event, or request a replay. The payment settlement was never delayed by the webhook delivery — the two systems are completely decoupled by the transactional outbox. Transactional outbox, delivery never blocks processing."))

    return lines
