#!/usr/bin/env python3
"""generate_mock_interview.py — Two-voice mock interview dialogue episodes.

Interviewer: en-US-AvaNeural (expressive, friendly)
Candidate: en-US-BrianNeural (casual, approachable)
Duration: 25-30 min per episode
Structure: 5 min requirements → 10 min high-level → 10 min deep dive → 3 min debrief
"""

import json, os, sys, subprocess, shutil, tempfile
from datetime import datetime, timezone

from tts import synthesize, get_duration_str, concatenate_mp3, crossfade_mp3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_BANK_PATH = os.path.join(SCRIPT_DIR, "content_bank.json")
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

MOCK_INTERVIEWS = [
    {
        "id": 46, "theme": "mock-payment-system",
        "title": "Mock Interview: Payment System",
        "subtitle": "Full 30-min mock system design interview",
        "playlist_id": "sd-mock-interviews",
        "item_id": "design-payment-system",
        "interviewer_style": "structured",
    },
    {
        "id": 47, "theme": "mock-url-shortener",
        "title": "Mock Interview: URL Shortener",
        "subtitle": "Full 25-min mock system design interview",
        "playlist_id": "sd-mock-interviews",
        "item_id": "design-url-shortener",
        "interviewer_style": "exploratory",
    },
    {
        "id": 48, "theme": "mock-news-feed",
        "title": "Mock Interview: News Feed",
        "subtitle": "Full 30-min mock system design interview",
        "playlist_id": "sd-mock-interviews",
        "item_id": "design-news-feed",
        "interviewer_style": "structured",
    },
]


def load_content_bank():
    with open(CONTENT_BANK_PATH) as f:
        return json.load(f)


def find_item(content_bank, item_id):
    for section in ["core_concepts", "case_studies", "architecture_patterns"]:
        for item in content_bank["system_design"].get(section, []):
            if item["id"] == item_id:
                return item
    return None


def build_interview_dialogue(item, config):
    """Generate two-voice interview dialogue from item data.

    Dispatches to a topic-specific builder based on the config theme,
    so each interview can have deep, realistic content for its domain.
    Target: ~4750 words of dialogue for ~30 min at 159 WPM.
    """
    theme = config.get("theme", "")
    if theme == "mock-payment-system":
        return _build_payment_system_interview(item, config)
    elif theme == "mock-url-shortener":
        return _build_url_shortener_interview(item, config)
    elif theme == "mock-news-feed":
        return _build_news_feed_interview(item, config)
    else:
        return _build_generic_interview(item, config)


def _build_payment_system_interview(item, config):
    lines = []

    # === SECTION 1: Intro & Requirements Clarification (~5 min) ===
    lines.append(("interviewer", "Hi, thanks for coming in today. I'm Ava, and I'll be conducting your system design interview. The problem we'll be working on is designing a payment system, something along the lines of what Stripe or Square provides. Before we dive into the design, I'd like you to start by clarifying the requirements. What questions would you want to ask the stakeholder?"))

    lines.append(("candidate", "Great, thanks for having me. So a payment system is a really broad topic, and the design changes significantly depending on the specifics, so let me ask some clarifying questions first. The most fundamental one: what type of payments are we processing? Are we talking about card payments, bank transfers, peer-to-peer, or a mix of everything? And are we building the full payment processing stack ourselves, or are we integrating with existing payment processors like Adyen or Stripe as a downstream provider?"))

    lines.append(("interviewer", "Good question to start with. Let's say we're building a payment gateway that integrates with payment processors. So we handle the merchant-facing API, manage the payment lifecycle, and then route to processors like Adyen or Worldpay downstream. We're not building the actual card network integration ourselves."))

    lines.append(("candidate", "OK that clarifies things a lot. So we're a layer between merchants and processors. Next I'd want to understand the scale. How many transactions per second are we handling at peak, and what's the daily volume? Also, what currencies and regions are we supporting, because that affects regulatory requirements like PCI DSS compliance."))

    lines.append(("interviewer", "Let's say we're handling about 10K transactions per second at peak, which works out to roughly 864 million transactions per day. We operate in multiple regions — US, EU, and APAC — and we need to support at least 50 currencies. And yes, PCI DSS compliance is a hard requirement."))

    lines.append(("candidate", "10K TPS is significant. That immediately tells me we need horizontal scaling and likely database sharding. Now let me ask about the payment lifecycle itself. Are we doing authorization and capture as separate steps, or is it auth-and-capture in one shot? Some merchants, like e-commerce platforms, want to authorize when the customer places the order but capture later when the item ships. And what about refunds and disputes — do we need to support partial refunds?"))

    lines.append(("interviewer", "We definitely need separate auth and capture. Merchants need that flexibility. And yes, we need full refund support including partial refunds, and we need to handle chargebacks and disputes that come back from the card networks. These can arrive days or even weeks after the original transaction."))

    lines.append(("candidate", "Right, so the payment can be in many different states over its lifetime. That's a state machine problem, which is one of the trickier parts. Let me also ask about reliability requirements. Payment systems are one of those areas where losing a transaction is not acceptable — we're talking about money. So what's our durability guarantee? And what about latency — merchants need to know if a payment was accepted in real time, right?"))

    lines.append(("interviewer", "Exactly right. We cannot lose a payment, period. The durability guarantee is that once we've acknowledged a payment to the merchant, it must be persisted even if a server crashes immediately after. For latency, the synchronous part — authorizing with the processor — needs to complete within a few seconds. The async parts like settlement and reconciliation can take longer. What other questions do you have?"))

    lines.append(("candidate", "Two more things. First, how do we handle idempotency? If a merchant's client has a network timeout and retries the same payment, we absolutely cannot charge the customer twice. I want to understand if we're building the idempotency mechanism ourselves or relying on the processor. Second, what about the financial ledger — do we need a double-entry bookkeeping system, or is a simpler transaction log sufficient?"))

    lines.append(("interviewer", "Both great points. We need to build idempotency ourselves — the merchant sends an idempotency key with each request, and we guarantee that the same key always returns the same result without double-processing. And yes, we need a proper double-entry ledger. Every financial movement needs to be recorded with matching debits and credits. This is non-negotiable for audit and regulatory reasons."))

    lines.append(("candidate", "OK, I think I have a clear enough picture now. Let me summarize what I understand. We're building a payment gateway that sits between merchants and downstream processors. We need to handle 10K TPS peak across multiple regions and currencies. The payment lifecycle includes auth, capture, refund, and dispute states. We need strong durability guarantees, client-side idempotency with keys, and a double-entry ledger for all financial movements. PCI DSS compliance is required. Let me move on to some back-of-envelope estimation."))

    # === SECTION 2: Back-of-Envelope Estimation (~5 min) ===
    lines.append(("interviewer", "Go ahead, walk me through the numbers."))

    lines.append(("candidate", "Alright, so let's start with throughput. We have 10K TPS at peak. The average TPS is probably much lower — peak to average ratio for payment systems is usually around 3 to 5x, so average is roughly 2 to 3K TPS. Over a day, 864 million transactions sounds about right. Now let me think about the read versus write ratio. For a payment system, reads are actually quite common — merchants checking payment status, dashboard queries, reconciliation lookups. I'd estimate a read to write ratio of about 5 to 1. So at peak, we're looking at 10K writes per second and about 50K reads per second."))

    lines.append(("interviewer", "Wait, you said 50K reads per second. Let me probe that a bit. Where are all those reads coming from?"))

    lines.append(("candidate", "Good point, let me think about that more carefully. The main read sources would be merchants querying payment status through our API, and that's probably one or two status checks per payment on average. Then there's the dashboard which polls for updates, and reconciliation queries that happen in batches. Actually, I think my 5 to 1 ratio might be too aggressive. Let me revise that to about 3 to 1. So 30K reads and 10K writes at peak. The dashboard and reconciliation queries can be served from a read replica or a separate analytics store, so they don't all hit the primary database."))

    lines.append(("interviewer", "OK, that sounds more reasonable. What about storage?"))

    lines.append(("candidate", "Right, storage. Each transaction record needs to store quite a bit of data. There's the payment ID, the idempotency key, the merchant ID, the amount, currency, payment method, the current state, timestamps for each state transition, the processor reference, and some metadata. I'd estimate about 500 bytes per transaction record. Then the ledger entries are separate — each payment generates at least two ledger entries for the double-entry, so that's another 300 bytes each times two, so 600 bytes per payment for ledger data. Plus we store audit logs. So roughly 1.5 KB per payment all in."))

    lines.append(("candidate", "Wait, I said the read QPS was 30K, but I forgot to account for the cache hit ratio. If we cache payment status in something like Redis and 80% of reads hit the cache, then only 20% reach the database, so the actual DB read QPS is about 6K, not 30K. That's much more manageable for the database layer. And for writes, there's no cache — every write has to hit the primary database because of the consistency requirements."))

    lines.append(("interviewer", "Good catch on the cache adjustment. So let me ask you about the storage math. Can you project this out over time?"))

    lines.append(("candidate", "Sure. At 864 million transactions per day and 1.5 KB each, that's about 1.2 terabytes per day. Wait, let me recalculate. 864 million times 1.5 KB is 864 million times 1500 bytes, which is about 1.3 times 10 to the 12 bytes, so roughly 1.2 terabytes per day. Hmm, that seems really high. Let me double-check my per-record estimate. Actually, I think 1.5 KB was too generous. A lot of fields are short — IDs are UUIDs at 36 bytes, amounts are 8 bytes, state is an enum at a few bytes. Let me revise to about 200 bytes for the payment record, 150 bytes per ledger entry times 2 equals 300 bytes, and 100 bytes for audit metadata. So more like 600 bytes per payment. That gives us 864 million times 600 bytes, which is roughly 500 gigabytes per day."))

    lines.append(("interviewer", "That's still a lot of data. What about retention?"))

    lines.append(("candidate", "Right, for regulatory reasons, financial records typically need to be retained for 7 years in most jurisdictions. But we don't need hot access to all 7 years of data. I'd design this with a tiered storage strategy. The last 90 days in the primary database for real-time queries and dashboards. The last year in a cheaper database or object store for occasional lookups and reconciliation. And anything older than a year goes to cold storage like S3 Glacier or similar, for compliance and audit purposes only. So the hot storage is roughly 500 GB per day times 90 days, which is about 45 terabytes. That's large but manageable with sharding."))

    # === SECTION 3: High-Level Architecture (~5 min) ===
    lines.append(("interviewer", "Good. Now let's move on to the high-level architecture. What are the main components, and how do they fit together?"))

    lines.append(("candidate", "Alright, let me draw this out. At the top, we have the merchant-facing API layer. This is a set of RESTful endpoints that merchants call to create payments, check status, process refunds, and so on. Behind the API layer, we have a load balancer distributing requests across multiple API servers. The API servers handle request validation, authentication, and idempotency checks before passing the request downstream."))

    lines.append(("candidate", "Next, we have the payment processing service. This is the core business logic layer. It manages the payment state machine — transitioning payments between states like pending, authorized, captured, failed, refunded, and disputed. It also orchestrates calls to the downstream payment processors. When a payment needs to be authorized, this service makes the API call to Adyen or Worldpay and updates the state based on the response."))

    lines.append(("interviewer", "Why have a separate payment processing service? Why not handle that logic in the API layer directly?"))

    lines.append(("candidate", "That's a fair question. There are a few reasons. First, separation of concerns — the API layer is responsible for request handling, validation, and routing, while the processing service handles the business logic and state management. This lets us scale them independently. The processing service might need to maintain long-running connections to payment processors, while the API layer needs to handle burst traffic. Second, it allows us to retry failed processor calls without the merchant's client needing to stay connected. The API can acknowledge the request, and the processing service handles retries asynchronously in the background."))

    lines.append(("interviewer", "OK, that makes sense. What about the data layer?"))

    lines.append(("candidate", "Right, so for the data layer, we have a few different stores. The primary database is a relational database like PostgreSQL, sharded by merchant ID. This stores the payment records and the ledger entries. We need relational consistency here because of the double-entry bookkeeping requirement — the debit and credit entries must be written atomically in a single transaction. We also have a Redis cluster for caching payment status, storing idempotency keys, and rate limiting. And then there's a message queue, something like Kafka, that publishes payment events — state changes, settlement notifications, and so on. Downstream consumers use these events for reconciliation, analytics, and notifications."))

    lines.append(("interviewer", "Walk me through why you need Kafka here. Couldn't you just poll the database for state changes?"))

    lines.append(("candidate", "You could, but polling the database for state changes is inefficient and introduces latency. With Kafka, the processing service publishes an event every time a payment state changes — something like a payment_authorized event with the payment ID, amount, and timestamp. Consumers like the reconciliation service, the merchant notification service, and the analytics pipeline all subscribe to these events and react in near real-time. It also decouples these services from the core processing path, so if the analytics pipeline is slow or down, it doesn't affect payment processing. The events are persisted in Kafka, so consumers can replay them if needed, which is important for recovery scenarios."))

    lines.append(("candidate", "One more component I should mention is the reconciliation service. This is a batch process that runs daily, comparing our internal ledger records against the settlement reports from the payment processors and bank statements. Discrepancies are flagged for manual review. This is critical for catching errors, missing transactions, or processor-side issues that might not surface through the real-time path."))

    # === SECTION 4: Deep Dive on Hardest Component — Payment State Machine & Idempotency (~8 min) ===
    lines.append(("interviewer", "Great overview. Now, which component do you think is the hardest to get right, and why?"))

    lines.append(("candidate", "Hmm, so let me think about this. The reconciliation process is tricky but it's a batch system, so there's some slack. The integration with processors is complex but it's mostly about handling their API quirks. I think the hardest part is the combination of the payment state machine and the idempotency mechanism, because these are where correctness really matters and the failure scenarios are subtle. If we get the state machine wrong, a payment could be captured twice. If idempotency fails, a merchant could double-charge a customer. So let me dive deep into those two interconnected pieces."))

    lines.append(("interviewer", "Sounds good. Let's start with the state machine. Walk me through the states and transitions."))

    lines.append(("candidate", "OK, so a payment starts in the PENDING state when it's first created. From PENDING, it transitions to AUTHORIZED when the processor confirms the funds are available and reserved. It can also go directly to FAILED if the processor rejects it — insufficient funds, card declined, that sort of thing. From AUTHORIZED, we can go to CAPTURED, which means the funds have actually been transferred. Or it can go to CANCELLED if the merchant decides to release the hold before capturing. From CAPTURED, we can transition to REFUNDED, which returns the money to the customer. And from CAPTURED or REFUNDED, we can go to DISPUTED if the customer initiates a chargeback."))

    lines.append(("interviewer", "What about partial refunds? A merchant might refund part of a captured payment and then refund the rest later."))

    lines.append(("candidate", "Right, I should have been more precise. Actually, the REFUNDED state isn't binary — we need to track the refunded amount separately. So the payment can be in a PARTIALLY_REFUNDED state when some but not all of the captured amount has been refunded, and FULLY_REFUNDED when the entire captured amount is returned. Let me define the data model to make this concrete. We'd have a payments table with columns: payment_id which is a UUID, idempotency_key which is a string, merchant_id, amount as an integer in the smallest currency unit to avoid floating point issues, currency as a three-letter code, payment_method which references a stored payment method, state as an enum, captured_amount which defaults to null and gets set on capture, refunded_amount which defaults to zero and increments on each refund, processor_reference which is the ID the downstream processor assigns, created_at, updated_at, and some metadata as a JSONB column for extensibility."))

    lines.append(("interviewer", "Why store amounts as integers in the smallest currency unit?"))

    lines.append(("candidate", "Floating point numbers are imprecise — 0.1 plus 0.2 doesn't equal 0.3 in floating point. In a financial system, that's unacceptable. So we store amounts as integers in cents, pence, or the smallest unit of the currency. For example, $19.99 is stored as 1999. When we need to display it, we divide by 100 and format with the appropriate decimal places. This eliminates rounding errors entirely."))

    lines.append(("interviewer", "Good. Now let's talk about the state transitions. How do you ensure that invalid transitions can't happen?"))

    lines.append(("candidate", "The state machine needs to enforce that only valid transitions are allowed. You can't go from FAILED to CAPTURED, for instance. I'd implement this as a validation check before any state update, something like a map of allowed transitions. From PENDING, you can go to AUTHORIZED or FAILED. From AUTHORIZED, you can go to CAPTURED or CANCELLED. From CAPTURED, you can go to PARTIALLY_REFUNDED or DISPUTED. And so on. If the code tries an invalid transition, it throws an error. But more importantly, this check needs to happen inside the database transaction that updates the state, to prevent race conditions. We use a compare-and-swap approach — the UPDATE statement includes a WHERE clause that checks the current state. For example, UPDATE payments SET state equals 'CAPTURED' WHERE payment_id equals X AND state equals 'AUTHORIZED'. If the row was already in a different state because of a concurrent request, the update affects zero rows, and we handle that as a conflict."))

    lines.append(("interviewer", "Now let's talk about idempotency. Walk me through exactly how it works when a merchant sends a payment request with an idempotency key."))

    lines.append(("candidate", "OK so the flow is like this. The merchant sends a POST request to the payments endpoint with an Idempotency-Key header. The API server first checks the idempotency store — which is a table in our database — to see if this key already exists. If it does, we look at the stored result. If the result is a success, we return the same successful response. If the result is still in progress, meaning the payment is being processed, we return a 202 Accepted indicating that the request is still being handled. If the key doesn't exist, we create a new entry in the idempotency table with status IN_PROGRESS, and then proceed to create the payment."))

    lines.append(("interviewer", "Walk me through exactly what happens in the database transaction. What tables are involved?"))

    lines.append(("candidate", "So this is where it gets interesting and where correctness really matters. The idempotency check and the payment creation need to happen atomically. Here's the transaction. We start a transaction. First, we INSERT into the idempotency_keys table — the table has columns for the key, the merchant_id, the status, and the result. We use ON CONFLICT DO NOTHING on the key column, which has a unique constraint. Then we check if the insert actually happened by checking the row count. If it's zero, the key already existed, so we SELECT the existing entry and return the stored result. If the insert succeeded, we proceed to INSERT into the payments table and the ledger_entries table for the double-entry record. Then we commit the transaction."))

    lines.append(("candidate", "Wait, actually I need to be more careful here. The problem is that the processor call — the actual authorization with Adyen or Worldpay — is an external API call that can take seconds. We can't hold a database transaction open while waiting for an external service. That would lock rows and kill our throughput. So the flow needs to be split. In the first transaction, we insert the idempotency key with status IN_PROGRESS and the payment record with state PENDING. Then we commit and make the processor call outside the transaction. When the processor responds, we start a second transaction to update the payment state and the idempotency result, then commit again. If the processor call times out or fails, the idempotency key remains in IN_PROGRESS state, and a retry will find it and wait or return 202."))

    lines.append(("interviewer", "What happens if the server crashes between the first commit and the processor call? The idempotency key is IN_PROGRESS but nobody is actually processing it."))

    lines.append(("candidate", "That's a great catch. We need a recovery mechanism for orphaned IN_PROGRESS entries. We'd have a background job that periodically scans for idempotency keys that have been IN_PROGRESS for longer than a timeout — say 5 minutes. When it finds one, it checks the corresponding payment state. If the payment is still PENDING, it means the processor call was never made or never completed. The background job would then query the processor to check the status using the processor reference if we have one, or simply mark the payment as FAILED and update the idempotency key result. The merchant can then retry with the same idempotency key, and since we've resolved the IN_PROGRESS entry, it'll be treated as a new request."))

    lines.append(("interviewer", "Now let's talk about the double-entry ledger. Why is it needed, and how does it work?"))

    lines.append(("candidate", "The double-entry ledger is the source of truth for all financial movements. Every time money moves, we record two entries — a debit and a credit — that must balance. For example, when a payment of $100 is captured, we debit the merchant's receivable account for $100 and credit the payment processor's liability account for $100. The merchant's account shows they're owed $100, and the processor's account shows they owe us $100 to settle. When settlement happens, we debit the processor's liability and credit our bank account. The key insight is that the sum of all accounts should always be zero — every debit has a matching credit. If it's not zero, something is wrong."))

    lines.append(("candidate", "The ledger_entries table would have: entry_id as a bigserial primary key, ledger_account which is an enum for accounts like merchant_receivable, processor_payable, platform_revenue, settlement, payment_id as a foreign key, amount as a positive integer, entry_type as either DEBIT or CREDIT, and created_at. The constraint is that for any payment, the sum of credits minus the sum of debits must equal zero. We enforce this at the application level within each transaction — when we write the payment record, we also write the corresponding ledger entries in the same transaction."))

    # === SECTION 5: Failure Modes & Reliability (~4 min) ===
    lines.append(("interviewer", "Let's shift gears and talk about failure modes. What are the most likely failures in this system, and how do you handle each one?"))

    lines.append(("candidate", "The first and most critical failure is the payment processor being unavailable or slow. If Adyen goes down, we can't authorize payments. For this, I'd implement a circuit breaker pattern around the processor client. If we get, say, 5 consecutive timeouts or errors within a 10-second window, the circuit breaker opens and we start failing fast instead of waiting for timeouts that will never resolve. We also need a fallback — we could route to an alternate processor if one is available, or we could queue the payment for retry when the processor comes back. The choice depends on the merchant's tolerance for latency versus rejection."))

    lines.append(("interviewer", "Walk me through exactly what happens when a write fails mid-transaction. Say the processor call succeeds, but the database commit for the state update fails."))

    lines.append(("candidate", "This is one of the scariest scenarios because the processor has authorized the payment, but our database doesn't know about it. The first line of defense is that we always record the processor's reference ID. When the database comes back up, the reconciliation service will detect the discrepancy — the processor says the payment was authorized, but our ledger doesn't have a matching entry. More immediately though, we should have a retry mechanism with an exponential backoff that re-attempts the database write. Since the payment ID is deterministic — it was generated in the first transaction — the retry will update the correct payment record. And if the first transaction's commit truly failed, the payment record won't exist yet, so the retry would need to handle both the INSERT and the UPDATE. Actually, this is why I like to separate the idempotency key creation from the state update. The idempotency key creation happens first, so even if the state update fails, the key exists and prevents duplicate submissions."))

    lines.append(("candidate", "Another failure mode is duplicate messages from Kafka. If the processing service publishes a payment_authorized event and the broker doesn't acknowledge it, the service might publish it again. Consumers need to be idempotent too — they should check if they've already processed that event. For the ledger, this is naturally handled because we write ledger entries keyed to the payment ID and entry type, so a duplicate event would just attempt an insert that conflicts and gets ignored. For other consumers, we'd use a processed_events table or a deduplication cache in Redis."))

    lines.append(("interviewer", "What about network partitions? If the database primary in one region goes down and a replica is promoted, could we lose in-flight transactions?"))

    lines.append(("candidate", "With synchronous replication, we wouldn't lose committed transactions because the primary waits for at least one replica to acknowledge the write before committing. But there's a performance cost — it adds latency to every write. For a payment system, I think that trade-off is worth it. We'd use synchronous replication for the primary database cluster within a region. If the primary fails, the promoted replica has all committed data. The only scenario where we could lose data is if the primary acknowledges a commit to the client but the replication hasn't completed — but with synchronous mode, that can't happen. The risk is actually the opposite direction: the primary might commit and then the client connection drops before it receives the acknowledgment. The client thinks the commit failed, but it actually succeeded. That's exactly what the idempotency mechanism handles — the retry will find the existing record."))

    # === SECTION 6: Scale-Up Discussion (~3 min) ===
    lines.append(("interviewer", "Let's talk about scale. What changes if we need to handle 10x the traffic?"))

    lines.append(("candidate", "At 100K TPS peak, which is 10x, the architecture needs significant changes. First, the database becomes the clear bottleneck. A single PostgreSQL shard can handle maybe 10 to 20K writes per second, so at 100K TPS we need at least 5 to 10 shards. We'd shard by merchant_id, and since merchants vary wildly in size, we'd need to carefully assign large merchants to their own shards to avoid hot spots. Something like Consistent Hashing wouldn't work well here because the distribution is so skewed — a single large merchant like an e-commerce platform could generate more traffic than thousands of small merchants combined."))

    lines.append(("candidate", "Second, the caching layer becomes more important. At 10x scale, the read QPS after cache would be 60K without caching, which is expensive. We'd want a multi-tier cache — a local in-memory cache like a LRU cache in each API server for the hottest keys, backed by a distributed Redis cluster for broader coverage. We'd also need to think about cache warming — when a new API server comes up, it shouldn't have a cold cache that sends all reads to the database. We could pre-warm it by replaying recent payment events from Kafka."))

    lines.append(("candidate", "Third, the Kafka cluster needs to scale too. At 100K events per second, we'd need more partitions for our topics. And the reconciliation process, which is currently a single batch job, might need to be parallelized — instead of one job scanning all payments, we'd run one reconciliation worker per database shard."))

    lines.append(("interviewer", "And what about 0.1x scale? If the traffic is much lower, what simplifies?"))

    lines.append(("candidate", "At 1K TPS peak, a lot of the complexity goes away. We can run on a single PostgreSQL instance with read replicas for the dashboards — no sharding needed. Redis is still useful for caching and rate limiting, but it can be a single node, not a cluster. Kafka is probably overkill at this scale — we could use something simpler like RabbitMQ or even a database-backed queue with a polling pattern. The idempotency mechanism stays the same because correctness doesn't scale down, but the reconciliation service could run as a simple cron job instead of a distributed system. And we'd probably run fewer microservices — maybe just the API service and a background worker, instead of separate services for processing, reconciliation, notifications, and so on. The key principle is: correctness requirements don't change with scale, but complexity for performance does."))

    # === SECTION 7: Debrief (~2 min) ===
    lines.append(("interviewer", "Alright, that covers the main areas. Let me give you some specific feedback. First, the positive: your requirements clarification was excellent. You asked about idempotency, the payment lifecycle, and the ledger unprompted — those are the things that separate a payment system from a generic CRUD app, and you identified them immediately. Your estimation work was solid too, especially the way you caught the cache-adjusted read QPS and revised your per-record size estimate. That shows real attention to detail."))

    lines.append(("interviewer", "For areas to improve: when you were describing the state machine, you initially missed partial refunds. In a real interview, it's better to explicitly ask the interviewer about partial operations rather than assuming binary states. Also, when you described the idempotency flow, your first version had the processor call inside the database transaction — you caught and corrected that yourself, which is great, but in an interview, try to get it right the first time by thinking through the constraints before you start writing the flow. Holding a transaction open for an external call is a common mistake, and interviewers will notice if you make it, even if you correct it later."))

    lines.append(("interviewer", "One more thing: you could have gone deeper on the reconciliation process. You mentioned it runs daily, but you didn't describe what happens when a discrepancy is found. The resolution workflow — automatic retries versus manual review, escalation paths, SLAs for resolution — is an important part of a payment system design. Overall though, strong performance. You demonstrated good system thinking, caught your own mistakes, and communicated your reasoning clearly. Thanks for your time."))

    lines.append(("candidate", "Thanks for the feedback. I definitely agree on the partial refunds point — I should have asked about that upfront. And you're right that I should have thought through the transaction boundary before laying out the flow. The reconciliation resolution workflow is something I'll study more. Appreciate the thorough feedback."))

    return lines


def _build_url_shortener_interview(item, config):
    lines = []

    # === SECTION 1: Intro & Requirements Clarification (~5 min) ===
    lines.append(("interviewer", "Hi, welcome. Today we'll be working on designing a URL shortener, something like Bitly. Before we jump into the design, let's start with requirements clarification. What would you like to know?"))

    lines.append(("candidate", "Thanks. A URL shortener seems straightforward on the surface, but there are some interesting design choices underneath. Let me start with the basics. What's the primary use case? Is this a consumer-facing product where anyone can create short links, or is it an enterprise service for marketing teams and businesses? And do we need custom aliases, or are auto-generated short codes sufficient?"))

    lines.append(("interviewer", "Let's go with a mix. The main use case is consumer-facing — anyone can paste a long URL and get a short one. But we also want to support custom aliases for premium users. For auto-generated codes, they should be as short as possible. What else?"))

    lines.append(("candidate", "OK, custom aliases add complexity because of the uniqueness constraint and potential for collisions with auto-generated codes. Let me ask about scale next. How many URLs are we shortening per day, and what's the read-to-write ratio? I'd expect reads — the redirects — to massively outnumber writes — the shortenings."))

    lines.append(("interviewer", "Good instinct. We're looking at about 100 million new URLs per day, and the read-to-write ratio is about 10 to 1. We need to handle billions of existing URLs — let's say 10 billion total."))

    lines.append(("candidate", "100 million writes and a billion reads per day. That's read-heavy for sure. Now let me ask about the redirect behavior. When someone clicks a short link, should we do a 301 permanent redirect or a 302 temporary redirect? A 301 means the browser caches the redirect, which is great for performance but means we can't track clicks. A 302 means every click goes through our servers, which lets us track analytics but adds latency."))

    lines.append(("interviewer", "We want analytics, so 302 is the way to go for now. But I want you to think about how we could support both — maybe 301 for some links and 302 for others."))

    lines.append(("candidate", "Got it. So the default is 302 for analytics tracking, but premium users could opt into 301 for performance. That's a nice product feature. Let me also ask about the analytics themselves. What kind of tracking do we need? Click counts, geographic data, referrers, time-based breakdowns? And do analytics need to be real-time, or is near-real-time or daily aggregation acceptable?"))

    lines.append(("interviewer", "We want click counts, geographic breakdown by country, top referrers, and time-based aggregates by hour and day. Real-time isn't required for the detailed analytics — near-real-time with a few minutes of delay is fine. But the total click count should be approximately real-time, say within 30 seconds."))

    lines.append(("candidate", "OK, that tells me we need two tiers of analytics — a fast approximate counter for total clicks, and a more detailed analytics pipeline for the breakdowns. I'm thinking something like a Redis counter for the real-time click count and an event stream to a batch analytics system for the detailed data. Let me also ask about availability and durability. If a short link stops working, that's a broken link on the internet — it's pretty bad. What's our uptime target?"))

    lines.append(("interviewer", "We need 99.99% uptime for the redirect service. That's about 50 minutes of downtime per year. For the shortening service, 99.9% is acceptable. And we can't lose existing mappings — once a short link is created, it must always resolve."))

    lines.append(("candidate", "So the redirect path is more critical than the creation path. That makes sense — a broken redirect is visible to end users, while a temporary inability to create new links just affects the creator. Two more questions. What's the maximum length of a long URL we need to support? And do we need link expiration, where a short link stops working after a certain time?"))

    lines.append(("interviewer", "Support URLs up to 2048 characters. And yes, we want optional expiration for users who want it, but the default should be that links never expire."))

    lines.append(("candidate", "Alright, let me summarize. We're building a consumer-facing URL shortener with 100 million writes and 1 billion reads per day, 10 billion existing URLs, 302 redirects by default for analytics, custom aliases for premium users, near-real-time click counting, detailed analytics with geographic and referrer breakdowns, 99.99% uptime for redirects, and optional link expiration. Let me move to estimation."))

    # === SECTION 2: Back-of-Envelope Estimation (~5 min) ===
    lines.append(("interviewer", "Go ahead, walk me through the numbers."))

    lines.append(("candidate", "So, 100 million new URLs per day. The write QPS is 100 million divided by 86400 seconds, which is roughly 1,160 writes per second on average. Peak is probably 2 to 3x that, so around 3,500 writes per second at peak. For reads at a 10 to 1 ratio, that's about 11,600 reads per second average, and 35,000 reads per second at peak."))

    lines.append(("candidate", "Wait, I think my read estimate is off. Let me reconsider. The 10 to 1 ratio means for every URL shortened, there are 10 redirects. But that's the ratio for new URLs. Existing URLs — the 10 billion that already exist — also generate reads. Popular links could get thousands of clicks per day. So the actual read QPS could be much higher. Let me approach this differently. If we assume each of the 10 billion existing URLs gets an average of 0.1 clicks per day, that's a billion reads from existing links, plus a billion reads from new links at the 10 to 1 ratio. So roughly 2 billion reads per day, which is about 23,000 reads per second average, and 70,000 at peak. That's more consistent with what I'd expect for a Bitly-scale service."))

    lines.append(("interviewer", "I like that you caught the mistake and revised. So what's the storage requirement?"))

    lines.append(("candidate", "Right, storage. Each URL mapping needs a short code, the long URL, creation timestamp, user ID if it's a registered user, an expiration timestamp if set, and maybe some flags like whether it's a custom alias or a premium link. The short code is maybe 7 characters, the long URL averages 500 bytes, and the metadata is maybe another 100 bytes. So roughly 600 bytes per entry. With 10 billion entries, that's 6 terabytes total. And we're adding 100 million per day, which is about 60 gigabytes per day of new data. Over 5 years, that's 60 GB times 365 times 5, which is roughly 110 terabytes. So we need to plan for around 120 terabytes of storage."))

    lines.append(("interviewer", "And what about the analytics storage?"))

    lines.append(("candidate", "Ah, good point. Analytics data is separate and potentially much larger. Each click generates an event with the short code, timestamp, IP address for geolocation, referrer header, and user agent. That's maybe 200 bytes per click event. With 2 billion clicks per day, that's 400 gigabytes of raw event data per day. We wouldn't store all of this in the hot database though — we'd stream it to an analytics pipeline, aggregate it, and discard the raw events after, say, 30 days. The aggregated data — daily click counts per link, per country, per referrer — would be much smaller, maybe a few terabytes total."))

    # === SECTION 3: High-Level Architecture (~5 min) ===
    lines.append(("interviewer", "OK, good. Let's move on to the architecture. What are the main components?"))

    lines.append(("candidate", "Let me lay out the high-level design. First, we have the API layer. Two main endpoints: POST to /shorten for creating short links, and GET to /{short_code} for redirects. The API servers are stateless and sit behind a load balancer, so we can scale them horizontally. The redirect endpoint is the critical path — it needs to be fast and highly available, so we optimize for that."))

    lines.append(("candidate", "Next is the ID generation service. This is responsible for producing unique short codes. There are a few strategies here — I'll dive deep into this later — but at a high level, it generates a 7-character base62 string that maps to the long URL. Then we have the storage layer, which is a key-value store where the key is the short code and the value contains the long URL and metadata. We'd use something like DynamoDB or Cassandra, or we could shard MySQL by the short code range. For caching, we have a Redis cluster in front of the storage layer to absorb the heavy read traffic. And finally, the analytics pipeline — an async event stream that captures click data and feeds it to an aggregation system."))

    lines.append(("interviewer", "Why would you choose a key-value store over a relational database for this?"))

    lines.append(("candidate", "The access pattern for the redirect path is extremely simple — it's always a lookup by the short code. There are no joins, no complex queries, no transactions needed for reads. A key-value store like DynamoDB is optimized for exactly this pattern: get by key with single-digit millisecond latency at any scale. It also handles horizontal scaling automatically with consistent hashing. A relational database would work too, but it's overkill for the redirect path, and we'd have to manage sharding ourselves. That said, the shorten endpoint, which creates new mappings, might benefit from transactional guarantees — especially for custom alias checking and creation, where we need to ensure uniqueness atomically."))

    lines.append(("interviewer", "Interesting. So you might use different data stores for different operations?"))

    lines.append(("candidate", "I could, but that adds complexity. Let me think about this more carefully. Actually, I think I'd go with a single storage system — DynamoDB or a sharded MySQL — and optimize the read path with caching. The write volume is low enough — 3,500 per second at peak — that any of these systems can handle it. The read volume is the challenge, and caching solves that. If 90% of reads hit the cache, the database only sees 7,000 reads per second at peak, which is very manageable. So I'd keep it simple with one store and a caching layer."))

    lines.append(("interviewer", "Makes sense. Walk me through what happens when a user clicks a short link."))

    lines.append(("candidate", "Sure. The user's browser sends a GET request to our domain with the short code. The load balancer routes it to an API server. The API server first checks the Redis cache for the short code. If it's a cache hit — and at our scale, 90% or more should be — we immediately return a 302 redirect with the long URL in the Location header. If it's a cache miss, we query the database, get the long URL, populate the cache for future requests, and then return the 302. In parallel, we fire off a click event to the analytics pipeline. This event is non-blocking — we don't wait for it to be processed before returning the redirect. The entire redirect path should complete in under 50 milliseconds for cache hits."))

    # === SECTION 4: Deep Dive — ID Generation & Caching with Stampede Protection (~8 min) ===
    lines.append(("interviewer", "Good. Now let's deep dive into the ID generation. There are several strategies — what are the options, and which would you choose?"))

    lines.append(("candidate", "There are three main strategies I'd consider. The first is using an auto-incrementing counter and encoding it in base62. Base62 uses characters 0 through 9, a through z, and A through Z — 62 characters total. With 7 characters, we can represent 62 to the 7th power values, which is about 3.5 trillion unique IDs. That's more than enough for our 10 billion URLs. The approach is simple — we maintain a global counter, increment it for each new URL, and encode the number in base62. The problem is that the global counter is a single point of contention and a single point of failure."))

    lines.append(("candidate", "The second approach is pre-generated random keys. We have a key generation service that generates random 7-character base62 strings in batches, checks them against the database for uniqueness, and stores them in a key pool. When the shorten service needs a new key, it just pops one from the pool. This eliminates the single point of contention, but it requires pre-checking for uniqueness, and the pool needs to be kept full. If the pool runs dry, the shorten service blocks, which is bad."))

    lines.append(("candidate", "The third approach is to compute a hash of the long URL and take the first 7 characters of the hash. This is deterministic — the same long URL always maps to the same short code. But it doesn't guarantee uniqueness because of hash collisions in 7 characters, and it means we can't have multiple short codes for the same long URL, which some users might want. Also, 7 characters of MD5 or SHA256 gives us only 62 to the 7 collision space, and with 10 billion URLs, the birthday paradox means collisions are likely."))

    lines.append(("interviewer", "So which one would you go with, and why?"))

    lines.append(("candidate", "Hmm, so let me think about the trade-offs. The auto-increment counter is the simplest and guarantees no collisions, but the global counter is a bottleneck. I could mitigate that by using range-based allocation — instead of a single counter, we have a coordinator that hands out ranges of numbers to different servers. Server 1 gets numbers 1 through 1 million, server 2 gets 1 million through 2 million, and so on. Each server can independently assign IDs from its range. When a server runs low, it requests a new range. This is how Instagram's ID generation works with their snowflake-like approach. The coordinator is still a single point, but it's only contacted occasionally for range allocation, not for every single ID."))

    lines.append(("candidate", "Actually, I think the best approach for our use case is a hybrid. For auto-generated codes, I'd use a range-based counter with base62 encoding. The coordinator is a lightweight service, maybe implemented with ZooKeeper or etcd, that manages the range allocations. For custom aliases, we simply check the database for uniqueness before inserting. If the custom alias is already taken, we return an error and ask the user to try again. The custom alias path doesn't need to be as fast as the auto-generated path because it's a user-facing operation where a few hundred milliseconds of latency is acceptable."))

    lines.append(("interviewer", "What about the base62 encoding specifically? Walk me through how you'd convert a number to a base62 string."))

    lines.append(("candidate", "Sure. It's like converting a number to any other base. We have an alphabet string — zero through nine, lowercase a through z, uppercase A through Z. To encode a number, we repeatedly take the number modulo 62 to get the current character index, then divide by 62 to move to the next position. We build the string from right to left. For example, the number 125 in base62 would be: 125 mod 62 is 1, which is the character '1'. Then 125 divided by 62 is 2. 2 mod 62 is 2, which is the character '2'. So 125 in base62 is '21'. For 7 characters, we pad with the zero character on the left. In code, it's a simple loop — maybe 10 lines of code."))

    lines.append(("interviewer", "Now let's talk about caching in more detail. You mentioned 90% cache hit rate. How would you handle a cache stampede, where a popular key expires and thousands of requests hit the database simultaneously?"))

    lines.append(("candidate", "Cache stampede is a real risk for a URL shortener, especially when a popular link's cache entry expires. Say a viral link is getting 1,000 requests per second, and the cache TTL expires. All 1,000 concurrent requests find a cache miss and simultaneously query the database. The database gets hammered with 1,000 identical queries, which can cause it to slow down or even crash, which causes more cache misses, and the problem cascades. There are a few strategies to prevent this. The most common is called cache stampede protection, or sometimes thundering herd protection. One approach is to use a distributed lock — when a cache miss occurs, the first request acquires a lock, queries the database, populates the cache, and releases the lock. Other requests that find the cache empty and can't acquire the lock either wait briefly or serve a slightly stale value. Redis has a SETNX command — set if not exists — that works well for this."))

    lines.append(("candidate", "Another approach is probabilistic early expiration. Each request, when it finds a cached value that's close to expiring — say, within the last 10% of its TTL — has a small probability of proactively refreshing the cache before it expires. This spreads the refresh across many requests over a longer time window instead of all at once. And a third approach is to never let cache entries truly expire — instead, we always refresh them in the background. When we read a cache entry, we check its age, and if it's old, we trigger an async refresh while still returning the current value. This ensures the cache always has data and never has a true miss for popular keys."))

    lines.append(("interviewer", "Which of these would you implement for our system?"))

    lines.append(("candidate", "I'd go with a combination. For the redirect path, I'd use probabilistic early expiration as the primary mechanism. It's simple to implement — just a few lines of code at the cache read layer — and it naturally prevents stampedes without adding locks that could become bottlenecks themselves. As a fallback, I'd also implement the distributed lock approach for cold-start scenarios where a key isn't in cache at all. If we deploy new API servers or restart the cache cluster, every key is a miss, and we need to prevent the resulting thundering herd. The lock ensures only a few requests per key hit the database, while the rest wait briefly."))

    lines.append(("candidate", "I should also mention the Redis key pattern we'd use. For redirect lookups, the key would be something like 'url:colon:shortcode', and the value would be a JSON string containing the long URL, the expiration timestamp if any, and the redirect type — 301 or 302. We'd set a TTL of, say, 24 hours on each key, with the probabilistic early refresh kicking in at around 22 hours. For the click counter, we'd use a Redis key like 'clicks:colon:shortcode' with an INCR command on each redirect. Redis INCR is atomic and very fast, so it can handle the click counting for even the most popular links."))

    lines.append(("interviewer", "Let's also dive into the analytics pipeline. You mentioned an async event stream for click data. Walk me through the full pipeline from click event to the dashboard a user sees."))

    lines.append(("candidate", "Sure. So when a redirect happens, the API server publishes a click event to a Kafka topic — let's call it 'url_clicks'. The event contains the short code, the timestamp, the IP address, the referrer header, and the user agent string. The Kafka topic is partitioned by the short code, which ensures that all events for the same URL land on the same partition. This is important because it allows us to do per-URL aggregation within a single consumer without needing a distributed aggregation step."))

    lines.append(("candidate", "Downstream of Kafka, we have two consumer groups. The first is the real-time counter consumer. This consumer reads events and increments the click count in Redis using INCRBY. It also updates a Redis HyperLogLog keyed by the short code to track unique visitors — HyperLogLog is a probabilistic data structure that estimates cardinality with about 0.8% error using only 12 KB of memory per key. So for each URL, we get both total clicks and approximate unique visitors in near-real-time."))

    lines.append(("candidate", "The second consumer group is the analytics aggregation consumer. This consumer reads events in micro-batches — maybe every 30 seconds — and writes aggregated records to an analytics database. The aggregated records have dimensions like the short code, the country derived from the IP address using a GeoIP database, the hour of the click, and the referrer domain. The metrics are click count and unique visitor count. We'd store these in a columnar database like ClickHouse, which is optimized for analytical queries over time-series data. When a user opens their analytics dashboard, the frontend queries an API that reads from ClickHouse, filtering by the user's short codes and the selected time range, and returns the breakdown by country, referrer, and time."))

    lines.append(("interviewer", "Why use two separate consumers instead of one that does both?"))

    lines.append(("candidate", "Separation of concerns and failure isolation. The real-time counter is on the critical path — if it falls behind, the click count shown on the dashboard becomes stale. So we keep it lightweight and fast, just doing Redis INCRBY calls. The analytics consumer does heavier work — GeoIP lookups, batch writes to ClickHouse — and it's acceptable if it falls a few minutes behind. If the analytics consumer has a bug or crashes, the real-time counter keeps working fine. And if the Redis counter gets corrupted, we can always rebuild it from the Kafka events, which are retained for several days. This is the same pattern that companies like DoorDash use — separate fast and slow paths for different quality-of-service requirements."))

    # === SECTION 5: Failure Modes & Reliability (~4 min) ===
    lines.append(("interviewer", "What are the key failure scenarios, and how does the system handle them?"))

    lines.append(("candidate", "The most critical failure is the cache going down. If Redis becomes unavailable, all reads fall through to the database, and at 70K read QPS peak, that would likely overwhelm it. The first mitigation is to run Redis in a cluster with multiple replicas, so a single node failure doesn't take down the whole cache. We'd use Redis Cluster with at least 3 masters and 3 replicas. If the entire Redis cluster goes down — which should be extremely rare — we'd have circuit breakers on the cache layer that detect the failure and switch to a degraded mode. In degraded mode, the API servers use a local in-memory LRU cache with a smaller capacity — maybe 100,000 entries per server — to absorb the most popular URLs. It's not as good as the distributed cache, but it prevents a complete outage."))

    lines.append(("interviewer", "What about the database going down?"))

    lines.append(("candidate", "For the database, we'd run with multi-region replication. The primary handles writes, and replicas handle reads. If the primary fails, a replica is promoted. The concern here is the write path — if we lose the primary and the replica doesn't have the latest writes, we could lose some newly created short links. But since the write QPS is relatively low at 3,500 per second, synchronous replication to at least one replica is feasible without significant latency impact. For the redirect path, even if the primary is down, replicas can still serve reads. The only scenario where redirects fail is if the entire database cluster is down, which shouldn't happen with proper multi-AZ deployment."))

    lines.append(("candidate", "Another failure scenario is the ID generation coordinator going down. If we're using the range-based counter approach, each server has a local pool of IDs from its allocated range. So even if the coordinator goes down, servers can continue generating IDs from their existing ranges for a while. A server with a range of 1 million IDs and a peak usage of 3,500 per second could operate independently for about 5 minutes. When the coordinator comes back, servers request new ranges. We'd also run the coordinator in a high-availability configuration — etcd and ZooKeeper both support leader election and can survive node failures."))

    lines.append(("interviewer", "How would you handle a situation where a short code is generated but the database write fails — for example, due to a uniqueness collision on a custom alias?"))

    lines.append(("candidate", "For auto-generated codes using the range-based counter, collisions are impossible because each number is used exactly once. For custom aliases, we use a conditional insert — INSERT IF NOT EXISTS — and if it fails because the alias is taken, we return a clear error to the user asking them to choose a different alias. The idempotency concern here is different from a payment system — we don't need idempotency keys because creating the same custom alias twice should fail the second time. But for auto-generated codes, if the database write fails after we've already consumed the ID from the range, we just skip that ID and move to the next one. Wasting a few IDs out of 3.5 trillion is negligible."))

    # === SECTION 6: Scale-Up Discussion (~3 min) ===
    lines.append(("interviewer", "How would your design change at 10x scale?"))

    lines.append(("candidate", "At 10 billion reads per day instead of 2 billion, the read path becomes even more dominant. The cache hit rate needs to be higher — 95% instead of 90% — to keep the database load manageable. I'd increase the Redis cluster size and potentially add a second caching tier using a CDN edge cache. Popular short links could be cached at CDN points of presence around the world, so the redirect doesn't even need to reach our servers. This would dramatically reduce latency for end users and further reduce load on our infrastructure. CloudFlare and Fastly both support programmatic edge logic that could handle the 302 redirect at the edge."))

    lines.append(("candidate", "For the database, 10 billion URLs growing at 1 billion per day means we'd need more shards. With DynamoDB, we'd increase the partition count and provisioned capacity. With MySQL, we'd add more shards and potentially introduce a routing layer that maps short code ranges to shards. The analytics pipeline would also need to scale — processing 10 billion click events per day requires a more robust stream processing system, potentially something like Flink instead of a simpler batch aggregation."))

    lines.append(("interviewer", "And at 0.1x scale, 10 million URLs per day?"))

    lines.append(("candidate", "At 10 million URLs per day, the system is much simpler. A single MySQL instance can handle the write volume, and the read volume of about 100 million per day is easily handled by a MySQL read replica with a modest Redis cache. The ID generation can be a simple auto-increment column in MySQL — no need for a separate range allocator or coordinator. For analytics, a simple batch process that aggregates click logs every hour would be sufficient — no need for a real-time stream processing pipeline. And we could run the entire system on a few servers in a single region. The core design stays the same, but we strip away the distributed systems complexity that's only needed at scale."))

    # === SECTION 7: Debrief (~2 min) ===
    lines.append(("interviewer", "Let me give you some feedback. The positives first: your requirements clarification was thorough — you asked about redirect types, analytics requirements, and custom aliases, all of which significantly affect the design. Your comparison of the three ID generation strategies was well-structured, and I liked that you proposed a hybrid approach instead of just picking one. The cache stampede discussion showed good operational awareness."))

    lines.append(("interviewer", "For improvements: when you were discussing the base62 encoding, you walked through a simple example, which was good. But I would have liked to see you address the security concern — sequential IDs in base62 are predictable. An attacker could enumerate short codes and scrape all URLs. You should have mentioned this and proposed a mitigation, like XORing the counter with a secret or using a non-sequential encoding scheme. Also, when discussing the analytics pipeline, you focused on the storage side but didn't describe the actual stream processing architecture — what system processes the events, how the aggregation queries work, and how the results are served to users. That's a significant component that deserved more detail."))

    lines.append(("interviewer", "Overall, solid interview. You demonstrated good breadth and reasonable depth. Work on thinking about security implications proactively, and make sure to follow through on describing the full architecture of every major component, not just the parts you're most comfortable with. Thanks for your time."))

    lines.append(("candidate", "Thanks for the feedback. The predictability of sequential base62 IDs is a really good point — I should have caught that. XOR encoding or using a hash-based approach would fix it. And I agree I should have gone deeper on the analytics pipeline architecture. I'll make sure to describe the full picture next time, including the stream processing, aggregation tables, and the serving layer."))

    return lines


def _build_news_feed_interview(item, config):
    lines = []

    # === SECTION 1: Intro & Requirements Clarification (~5 min) ===
    lines.append(("interviewer", "Hi, welcome. Today we'll design a news feed system, like Twitter or Instagram. Let's start with requirements clarification. What questions do you have?"))

    lines.append(("candidate", "Thanks. A news feed is one of those systems that seems simple from the user's perspective — you just see a list of posts — but the engineering underneath is really interesting. Let me start with the most fundamental question: is the feed chronological, meaning the newest posts appear first, or is it ranked by an algorithm that considers relevance and engagement? Because the architecture for these two is quite different."))

    lines.append(("interviewer", "Great question to start with. Let's start with chronological as the baseline, but then I want you to extend the design to support algorithmic ranking. So design for both."))

    lines.append(("candidate", "OK, that's a nice progression. So chronological first, then add ranking. Next I'd want to understand the scale. How many daily active users are we talking about? And what's the average number of followers and followees per user? The ratio matters a lot for the fan-out strategy."))

    lines.append(("interviewer", "We're looking at 100 million daily active users, with about 500 million posts created per day. The average user follows about 200 people, but the distribution is very skewed — some users have millions of followers."))

    lines.append(("candidate", "100 million DAU and 500 million posts per day — that's significant. The skew in follower count is important because a user with 10 million followers means every post they create needs to be delivered to 10 million feeds. That's the classic fan-out problem. Let me ask a few more questions about the feed itself. How many posts are shown per page? Do we support infinite scroll with pagination? And when a user loads their feed, how fresh should it be — can it be a few seconds stale, or does it need to be real-time?"))

    lines.append(("interviewer", "We show about 20 posts per page, with infinite scroll pagination. The feed should be near-real-time — a new post from someone you follow should appear within about 5 seconds. Not hard real-time, but close."))

    lines.append(("candidate", "Near-real-time with 5 seconds freshness. That rules out fully pre-computed feeds that only update periodically, but it's still compatible with a push-based approach with a slight delay. Let me also ask about the types of content. Are we just dealing with text posts, or do we have images, videos, and link previews? Media content affects the data model and the ranking algorithm."))

    lines.append(("interviewer", "Primarily text posts, but we need to support images and link previews. Video is out of scope for now."))

    lines.append(("candidate", "Got it. And one more question about the social graph. Is the follow relationship symmetric, like Facebook friends, or asymmetric, like Twitter where you can follow someone who doesn't follow you back? This affects the fan-out direction."))

    lines.append(("interviewer", "Asymmetric — like Twitter. You can follow anyone, and they don't need to follow you back."))

    lines.append(("candidate", "OK, let me summarize. We're designing an asymmetric-follow news feed with 100 million DAU, 500 million posts per day, average 200 followings per user but with high skew, chronological baseline with algorithmic ranking extension, 20 posts per page with infinite scroll, near-real-time freshness within 5 seconds, supporting text and images. Let me move to estimation."))

    # === SECTION 2: Back-of-Envelope Estimation (~5 min) ===
    lines.append(("interviewer", "Walk me through the numbers."))

    lines.append(("candidate", "Let's start with the write side — 500 million posts per day. That's about 5,800 posts per second on average. Peak might be 3x, so around 17,000 posts per second at peak. Now here's where it gets interesting. Each post doesn't just write to one place — it potentially needs to be fanned out to all followers' feeds. With an average of 200 followers per user, the average fan-out write per post is 200. So the total fan-out write volume is 500 million times 200, which is 100 billion feed entries per day, or about 1.16 million writes per second. That's enormous. But wait, this is only if we use the fan-out-on-write approach. If we use fan-out-on-read, the write volume is just the 5,800 posts per second, but the read computation becomes expensive."))

    lines.append(("interviewer", "Good, you're already thinking about the trade-off. What about the read side?"))

    lines.append(("candidate", "Right. For reads, let's estimate how many feed requests we get. If 100 million DAU each load their feed maybe 10 times per day, that's a billion feed requests per day, or about 11,600 feed requests per second average, and 35,000 at peak. Each feed request returns 20 posts. Under fan-out-on-write, the read is just a lookup — fetch the top 20 items from the user's pre-computed feed. Under fan-out-on-read, each feed request requires querying the posts of all 200 people the user follows, merging them, and sorting by time. That's 200 queries per feed request, which at 35,000 feed requests per second is 7 million queries per second against the posts database. Clearly, fan-out-on-read at this scale needs heavy caching."))

    lines.append(("interviewer", "So which approach would you lean towards?"))

    lines.append(("candidate", "Hmm, let me think about this. The pure fan-out-on-write approach has the problem with celebrity users — a single post by someone with 10 million followers requires 10 million feed writes, which could take seconds and consume massive resources. Twitter actually moved away from pure fan-out-on-write for this reason. Instagram uses a hybrid approach. I think the hybrid is the way to go — fan-out-on-write for regular users with up to, say, 500 followers, and fan-out-on-read for celebrity users with more followers. Let me work out the numbers. If, say, 1% of users are celebrities with over 500 followers, that's 1 million celebrity users. The remaining 99% use fan-out-on-write. For regular users, the fan-out volume is manageable — most posts only need a few hundred feed writes. For celebrity posts, we skip the fan-out entirely and instead query their posts at read time. This caps the write amplification and keeps reads fast for the common case."))

    # === SECTION 3: High-Level Architecture (~5 min) ===
    lines.append(("interviewer", "OK, let's flesh out the architecture. What are the main components?"))

    lines.append(("candidate", "I'll lay out the components for the hybrid fan-out approach. First, we have the post service, which handles creating and storing posts. When a user creates a post, the post service writes the post to the posts database and then publishes a post_created event to a message queue like Kafka."))

    lines.append(("candidate", "Next is the fan-out service, which consumes the post_created events from Kafka. For each post, it checks the author's follower count. If the author has fewer than 500 followers, it pushes the post ID to each follower's feed timeline in a Redis sorted set, where the score is the post's timestamp. If the author has 500 or more followers, it skips the fan-out — the post will be pulled at read time instead. This threshold is configurable. The feed timeline in Redis is keyed by the user ID, and it stores the most recent post IDs — we'd keep maybe the latest 1,000 post IDs per user, which covers several pages of feed."))

    lines.append(("interviewer", "Why use a sorted set in Redis for the feed timeline? Why not just a list?"))

    lines.append(("candidate", "A sorted set lets us use the post timestamp as the score, which makes it easy to retrieve posts in chronological order and to do range queries for pagination. With a list, we'd have to maintain the order ourselves, and pagination would be tricky. A sorted set also naturally handles deduplication — if the same post ID is added twice, it just updates the score instead of creating a duplicate entry. This can happen if a fan-out-on-write delivery overlaps with a fan-out-on-read query for a celebrity who the user also follows. The ZREVRANGE command gives us the most recent post IDs in descending timestamp order, and ZRANGEBYSCORE with a cursor gives us the next page."))

    lines.append(("candidate", "Then there's the feed service, which handles feed read requests. When a user requests their feed, the feed service first fetches post IDs from the user's Redis timeline using ZREVRANGE. Then it fetches the full post data for those IDs from a posts cache or the posts database. But wait — there's a gap. The Redis timeline only contains posts from non-celebrity followings that were pushed via fan-out-on-write. For celebrity followings, we need to also pull their recent posts and merge them in. So the feed service also maintains the user's followee list, identifies which followees are celebrities, and queries their recent posts from the posts database or cache. It then merges the pushed posts and the pulled posts, sorts by timestamp, and returns the top 20."))

    lines.append(("interviewer", "That sounds expensive — querying celebrity posts on every feed request. How would you make that fast?"))

    lines.append(("candidate", "You're right, querying celebrity posts on every feed request would be too slow. I'd cache the recent posts of each celebrity in a separate Redis key — something like 'celebrity:colon:user_id:recent_posts' — storing the last, say, 100 post IDs. Since celebrity posts are highly read, this cache would have an extremely high hit rate. The fan-out service updates this cache whenever a celebrity posts. So the feed service just reads from this cache, which is fast. The number of celebrities is small — maybe 100,000 users — so caching their recent posts is very affordable in terms of memory."))

    # === SECTION 4: Deep Dive — Fan-Out Strategies & Ranking (~8 min) ===
    lines.append(("interviewer", "Let's deep dive into the fan-out strategies more carefully. You described the hybrid approach, but I want to understand the edge cases. What happens when a user who was previously a regular user becomes a celebrity — they cross the 500 follower threshold?"))

    lines.append(("candidate", "That's a really important edge case, and it's one that Bitly and Twitter both had to deal with. When a user crosses the threshold, we need to transition them from fan-out-on-write to fan-out-on-read. The problem is that their existing posts are already fanned out to some followers' timelines, but not all — specifically, they're in the timelines of followers who started following them before the transition, but not in the timelines of new followers. We need a migration process. When the threshold is crossed, we'd run a background job that removes all of this user's posts from every follower's timeline, and starts caching their posts as celebrity posts. During the transition period, which might take a few minutes, some followers might see duplicate posts — once from their timeline and once from the celebrity pull. But the sorted set deduplication handles this naturally, since the same post ID with the same timestamp score is only stored once."))

    lines.append(("interviewer", "What about the reverse — a celebrity who loses followers and drops below the threshold?"))

    lines.append(("candidate", "That's rarer but possible. In that case, we'd transition them back to fan-out-on-write. The fan-out service would start pushing their new posts to all followers' timelines again. We'd also need to backfill their recent posts into followers' timelines — the last few hundred posts or so, enough to cover several pages of feed. This backfill could be done lazily — we only need to populate a follower's timeline when they actually load their feed, and we can check for missing posts at that point. Actually, that's a nice optimization in general — rather than eagerly ensuring every timeline is perfectly consistent, we can do lazy repair on read. When the feed service detects that a timeline is missing expected posts, it adds them."))

    lines.append(("interviewer", "Now let's talk about the ranking algorithm. You said the feed starts as chronological and extends to algorithmic. Walk me through how you'd implement ranking."))

    lines.append(("candidate", "For the ranked feed, we need to assign a score to each post that determines its position in the feed. A simple scoring function might look like: score equals w1 times recency plus w2 times engagement plus w3 times author affinity. Recency is a decreasing function of the post's age — something like exponential decay, where the score halves every few hours. Engagement includes likes, retweets, and comments, weighted differently — a retweet is worth more than a like because it indicates stronger interest. Author affinity measures how often the user interacts with the author's posts — if you frequently like and comment on someone's posts, their posts get a higher score in your feed."))

    lines.append(("candidate", "The challenge is computing this score efficiently. Some factors, like recency, can be computed at post creation time. Others, like engagement, change over time as people interact with the post. And author affinity is specific to each user-post pair, so it can't be pre-computed globally. Instagram uses a approach where they pre-compute a candidate set of posts and then score them at request time. The candidate set comes from the pre-computed feed timeline, and the scoring is fast because it only needs to score the top 100 or so candidates, not the entire feed. The final 20 posts shown to the user are the top-scoring 20 from this candidate set."))

    lines.append(("interviewer", "How would you handle the fact that engagement scores change over time? A post that has 10 likes when it enters the feed might have 10,000 likes an hour later."))

    lines.append(("candidate", "Right, so the score stored in the sorted set at fan-out time might be stale by the time the user loads their feed. There are a few approaches. The simplest is to periodically update the scores — we could have a background job that recalculates engagement scores for the most recent posts every few minutes and updates the sorted set entries. Another approach is to split the scoring into a static component and a dynamic component. The static component — recency and pre-computed author affinity — is stored in the sorted set score. The dynamic component — current engagement — is looked up at read time and combined with the static score. This way, we get fresh engagement data without having to update every sorted set entry. The trade-off is that we need an additional lookup per post at read time, but since we're only looking up 20 to 100 posts per feed request, it's manageable."))

    lines.append(("interviewer", "Let's also talk about pagination in detail. You mentioned cursor-based pagination, but I want you to walk me through exactly how it works, especially for a feed where new posts are constantly arriving."))

    lines.append(("candidate", "Good, this is really important and I should have been more explicit. The problem with offset-based pagination — like saying give me posts 1 through 20, then 21 through 40 — is that new posts are constantly being inserted at the top of the feed. If a user is viewing page 2 and 5 new posts arrive at the top, the offset shifts and the user would see 5 posts from page 1 repeated on page 2. That's a terrible user experience. Cursor-based pagination solves this by using the last post the user has seen as the anchor. Specifically, we use the post's creation timestamp and its ID as the cursor. The API request includes a cursor parameter like 'cursor equals 1700000000_abc123', where the first part is the timestamp and the second is the post ID."))

    lines.append(("candidate", "On the server side, the feed service queries the Redis sorted set using ZRANGEBYSCORE with the cursor timestamp as the upper bound, and a limit of 20. The query looks like ZRANGEBYSCORE feed:colon:userid minus_inf cursor_timestamp LIMIT 0 21. We fetch 21 items instead of 20 so we know whether there's a next page. If multiple posts share the same timestamp — which happens when several people post at the same second — we use the post ID as a tiebreaker. The post ID is a monotonically increasing value, so it guarantees a total ordering. The response includes the posts and a next_cursor field that the client sends back to fetch the next page. This approach is stable regardless of how many new posts arrive between page loads, because we're always fetching posts older than a specific anchor point, not relative to the top of the feed."))

    lines.append(("interviewer", "What happens when a user scrolls back up and then scrolls down again? They've already seen the first page — does the client need to re-fetch it?"))

    lines.append(("candidate", "That's a great practical question. The client should cache the posts it's already received in memory, so scrolling back up just renders from the local cache. But the user might want to see if new posts have arrived at the top. For that, we'd implement a pull-to-refresh gesture that fetches the latest posts — something like ZREVRANGE feed:colon:userid 0 20 — and prepends any new ones to the top of the local cache. The client tracks the most recent post timestamp it has, and the pull-to-refresh only fetches posts newer than that. This way, refreshing is efficient — it only fetches a few new posts, not the entire feed. Instagram and Twitter both use this pattern — the 'new posts' notification at the top of the feed is essentially telling the user that there are posts newer than their most recent cached timestamp."))

    # === SECTION 5: Failure Modes & Reliability (~4 min) ===
    lines.append(("interviewer", "Let's talk about failure modes. What happens when the Redis cluster that stores the feed timelines goes down?"))

    lines.append(("candidate", "That's a serious failure because the feed timelines are the primary data structure for serving feeds. If Redis is down, we'd fall back to a fan-out-on-read approach for all users, not just celebrities. The feed service would query the posts database for each of the user's followees, merge and sort the results. This would be slower — maybe 500 milliseconds to a second instead of the usual 50 milliseconds — but it would still work. To make this fallback feasible, we'd need the posts database to support efficient queries by author ID sorted by creation time, which is a natural index to have. We'd also need to rate-limit feed requests during the fallback to prevent the database from being overwhelmed."))

    lines.append(("interviewer", "What about the fan-out service going down? If it can't push posts to timelines, what happens?"))

    lines.append(("candidate", "If the fan-out service is down, new posts from regular users won't be pushed to followers' timelines. Followers would see stale feeds that don't include the latest posts. But the posts are still in the posts database — they just haven't been distributed. When the fan-out service comes back up, it can process the backlog of post_created events from Kafka, which has been buffering them. Kafka retention is typically set to several days, so we wouldn't lose any events. The feeds would eventually catch up. During the outage, we could also switch to a hybrid approach where the feed service pulls recent posts from the database for all followees, not just celebrities, as a temporary measure."))

    lines.append(("candidate", "Another failure scenario I should mention is a hot partition in the posts database. If a celebrity posts and millions of users try to load their feed simultaneously, the celebrity's recent posts cache becomes a hot key in Redis. To handle this, we'd use read replicas for the hot key — we can create multiple copies of the celebrity's recent posts key and distribute reads across them. Another technique is local caching — each feed server can cache celebrity posts in its local memory, so repeated requests for the same celebrity's posts don't all hit Redis. This is similar to how social networks handle the Justin Bieber problem, where a single user's activity can generate disproportionate load."))

    lines.append(("interviewer", "How would you ensure idempotency in the fan-out service? If Kafka delivers a duplicate post_created event, what prevents double-posting in a user's feed?"))

    lines.append(("candidate", "The sorted set naturally handles this. When we add a post ID to a user's timeline with ZADD, if the post ID already exists in the sorted set, the command just updates the score without creating a duplicate. So duplicate events from Kafka are harmless — the same post ID is added to the same timeline, and the sorted set remains consistent. This is one of the nice properties of using a sorted set for the timeline. If we had used a list instead, duplicates would be a real problem, and we'd need explicit deduplication logic."))

    lines.append(("interviewer", "What about the posts database itself — what data model would you use, and how would it handle the write volume?"))

    lines.append(("candidate", "The posts database stores every post ever created — 500 million per day. The table schema would include post_id as the primary key, author_id as a foreign key to the users table, content as a text field for the post text, media_urls as a JSON array for image references, created_at as a timestamp with an index, and some metadata like reply_count, like_count, and repost_count. The critical index is on author_id plus created_at — this is the index used by the fan-out-on-read path to fetch a celebrity's recent posts. We'd shard the posts database by author_id using a hash-based sharding strategy, so all posts by the same author live on the same shard. This makes the author-based queries efficient — they never cross shard boundaries."))

    lines.append(("candidate", "For the write volume, 5,800 posts per second is manageable with a moderately sized sharded database. Each shard handles a fraction of the total writes. We'd use a write-optimized database like Cassandra or a sharded MySQL cluster with write batching. Cassandra is attractive here because it handles time-series data well and supports tunable consistency — we can use QUORUM consistency for writes to ensure durability, and ONE consistency for reads when serving feeds, which is fast. The trade-off is that MySQL gives us strong consistency and transactions, while Cassandra gives us better write throughput and easier horizontal scaling. For a social feed where a slightly stale post is acceptable, I'd lean towards Cassandra."))

    # === SECTION 6: Scale-Up Discussion (~3 min) ===
    lines.append(("interviewer", "What changes at 10x the scale — a billion DAU?"))

    lines.append(("candidate", "At a billion DAU, the numbers become staggering. 5 billion posts per day, and the fan-out volume — assuming the hybrid approach — could be in the trillions of timeline writes per day. The Redis cluster would need to be massive. At this scale, I'd consider moving the feed timelines from Redis to a custom storage system optimized for this specific access pattern. Something like a write-optimized log-structured merge tree that can handle the massive write volume. We'd also need to shard the timelines more aggressively — instead of storing all timelines in one Redis cluster, we'd partition them by user ID ranges across multiple independent clusters. This also improves fault isolation — if one cluster fails, only a fraction of users are affected."))

    lines.append(("candidate", "For the ranking algorithm, at a billion users, computing personalized scores for every user-post pair is prohibitively expensive. We'd need to move to a two-phase ranking approach. The first phase is a lightweight pre-filter that selects candidate posts using simple, fast criteria. The second phase is a more expensive ML model that scores only the candidates. This is how production systems like Instagram and TikTok work — the retrieval layer narrows down millions of potential posts to a few hundred candidates, and then the ranking layer scores those candidates with a deep model."))

    lines.append(("interviewer", "And at 0.1x scale, 10 million DAU?"))

    lines.append(("candidate", "At 10 million DAU, the system is much more manageable. With 50 million posts per day and an average of 200 followers, the fan-out volume is 10 billion timeline writes per day, or about 115,000 per second. A single large Redis cluster can handle this. The hybrid approach isn't strictly necessary at this scale — we could use pure fan-out-on-write and just accept that occasional celebrity posts will cause a spike in write volume. For ranking, a simple recency-based sort with a few basic engagement signals would suffice — no need for a complex ML model. And we could run the entire system in a single region with multi-AZ redundancy, instead of multi-region."))

    lines.append(("candidate", "Actually, let me reconsider. Even at 10 million DAU, if we have a few users with, say, 100,000 followers each, fan-out-on-write for those users would still generate 100,000 timeline writes per post. At, say, 5 posts per day for each such user, that's half a million writes per power user per day. With maybe 100 such power users, we'd add 50 million extra timeline writes per day. That's still fine for Redis, but it's worth monitoring. I'd set the celebrity threshold lower at this scale — maybe 1,000 followers instead of 500 — and re-evaluate as we grow. The nice thing about the hybrid approach is that the threshold is a tuning knob, not an architectural change. We can adjust it without rewriting the system."))

    lines.append(("candidate", "One more simplification at 0.1x scale: we don't need a separate Kafka cluster for the fan-out service. The fan-out could happen synchronously within the post service — after writing the post to the database, we iterate over the author's followers and push to their timelines in the same request. This is simpler to implement and operate, though it increases the latency of the post creation endpoint. At 50 million posts per day with an average of 200 followers, the synchronous fan-out would add maybe 50 to 100 milliseconds to each post creation, which is acceptable. We'd only introduce the async Kafka-based fan-out when the synchronous approach becomes a bottleneck."))

    # === SECTION 7: Debrief (~2 min) ===
    lines.append(("interviewer", "Let me give you some specific feedback. The positives: your requirements clarification was thorough and well-prioritized. Asking about chronological versus algorithmic ranking upfront was smart — it fundamentally changes the architecture. Your explanation of the hybrid fan-out approach was clear, and you identified the transition edge case when a user crosses the celebrity threshold, which shows good operational thinking. The way you leveraged the sorted set properties for deduplication was a nice practical detail."))

    lines.append(("interviewer", "For improvements: when you described the feed service merging pushed and pulled posts, you initially didn't address how to make the celebrity pull fast. The interviewer had to prompt you to think about caching celebrity posts. In a real interview, try to identify performance bottlenecks in your own design before the interviewer points them out. Also, when discussing the ranking algorithm, you described the scoring function at a high level but didn't walk through a concrete example with numbers. Showing the interviewer how the weights work with specific values makes the algorithm much more tangible and demonstrates that you understand the implementation details, not just the concept."))

    lines.append(("interviewer", "One more thing: your cursor-based pagination explanation was thorough, including the pull-to-refresh pattern and the stability guarantees. That was well done. Overall, strong performance. Thanks for your time."))

    lines.append(("candidate", "Thanks for the feedback. The celebrity caching gap was a real miss — I should have thought through the full read path and identified that bottleneck myself. And you're absolutely right about the ranking example with concrete numbers — I should have walked through a specific calculation. I'll practice making my algorithm explanations more tangible. Appreciate the detailed feedback."))

    return lines


def _build_generic_interview(item, config):
    """Fallback generic interview builder for themes not explicitly handled."""
    name = item["name"]
    desc = item.get("description", "")
    components = item.get("key_components", [])
    estimates = item.get("estimates", "")
    bottlenecks = item.get("bottlenecks", "")

    lines = []

    lines.append(("interviewer", "Hi, thanks for coming in today. I'd like to do a system design interview with you. The problem is: design a system for " + name + ". Before we dive in, how would you approach this?"))

    lines.append(("candidate", "Great, thanks. So before I start designing, let me clarify the requirements. What's the primary use case, and what scale are we talking about?"))

    lines.append(("interviewer", desc + " " + (estimates if estimates else "Let's say medium scale.") + " What other questions do you have?"))

    lines.append(("candidate", "I'd want to know about latency requirements, availability needs, and consistency guarantees. Also, what are the key features we need to support?"))

    lines.append(("interviewer", "For latency, keep it responsive. Availability at 99.9%. Consistency depends on the operation. What components would you need?"))

    if components:
        lines.append(("candidate", "Looking at the key components: " + ", ".join(components[:3]) + ". Let me think about how they fit together."))
    else:
        lines.append(("candidate", "I'd need an API layer, a processing service, a database, and a caching layer. Let me think about how they fit together."))

    lines.append(("interviewer", "What's the hardest part of this design?"))

    if bottlenecks:
        lines.append(("candidate", "I think the main challenge is " + bottlenecks.split(".")[0].lower() + ". I'd address this with horizontal scaling and caching at the read layer."))
    else:
        lines.append(("candidate", "I think maintaining consistency under load is the hardest part. I'd use caching for reads and async queues for writes."))

    lines.append(("interviewer", "What about failure modes and scaling?"))

    lines.append(("candidate", "For failures, I'd use circuit breakers to prevent cascading issues and bulkhead patterns to isolate resources. For scaling at 10x, I'd shard the database and add more caching. At 0.1x, I'd simplify to a single server with no distributed components."))

    lines.append(("interviewer", "Alright, let me give you feedback. You did a good job with requirements and estimation. For improvement, be more specific about data models and API contracts in the deep dive. Thanks for your time."))

    lines.append(("candidate", "Thanks, I appreciate the feedback."))

    return lines


def generate_episode(config, content_bank):
    """Generate a complete mock interview episode."""
    item = find_item(content_bank, config["item_id"])
    if not item:
        print(f"  WARNING: Item {config['item_id']} not found")
        return None

    dialogue = build_interview_dialogue(item, config)

    # Split into interviewer and candidate segments
    interviewer_segments = []
    candidate_segments = []

    current_speaker = None
    current_text = []

    for speaker, text in dialogue:
        if speaker != current_speaker:
            if current_speaker and current_text:
                segment_text = " ".join(current_text)
                if current_speaker == "interviewer":
                    interviewer_segments.append(segment_text)
                else:
                    candidate_segments.append(segment_text)
            current_speaker = speaker
            current_text = [text]
        else:
            current_text.append(text)

    if current_speaker and current_text:
        segment_text = " ".join(current_text)
        if current_speaker == "interviewer":
            interviewer_segments.append(segment_text)
        else:
            candidate_segments.append(segment_text)

    # Generate audio for each speaker alternately, then interleave
    temp_dir = tempfile.mkdtemp(prefix="mock_interview_")
    segment_paths = []

    interviewer_idx = 0
    candidate_idx = 0
    turn = "interviewer"

    for speaker, text in dialogue:
        seg_idx = interviewer_idx if speaker == "interviewer" else candidate_idx
        seg_path = os.path.join(temp_dir, f"seg_{len(segment_paths):04d}.mp3")
        voice = "interviewer" if speaker == "interviewer" else "narrator"
        synthesize(text, seg_path, voice=voice, preprocess=True)
        segment_paths.append(seg_path)

        if speaker == "interviewer":
            interviewer_idx += 1
        else:
            candidate_idx += 1

    # Concatenate all segments
    mp3_path = os.path.join(DATA_DIR, f"mock-{config['theme']}.mp3")
    if len(segment_paths) == 1:
        shutil.move(segment_paths[0], mp3_path)
    else:
        concatenate_mp3(segment_paths, mp3_path)

    shutil.rmtree(temp_dir, ignore_errors=True)

    # Also save the script
    script_path = os.path.join(DATA_DIR, f"mock-{config['theme']}.txt")
    script_lines = []
    for speaker, text in dialogue:
        label = "INTERVIEWER" if speaker == "interviewer" else "CANDIDATE"
        script_lines.append(f"[{label}] {text}")
        script_lines.append("")

    with open(script_path, "w") as f:
        f.write("\n".join(script_lines))

    return {
        "id": config["id"],
        "theme": config["theme"],
        "title": config["title"],
        "subtitle": config["subtitle"],
        "playlist_id": config["playlist_id"],
        "mp3_path": mp3_path,
        "script_path": script_path,
        "file_size_bytes": os.path.getsize(mp3_path),
        "duration": get_duration_str(mp3_path),
    }


def main():
    print("=== generate_mock_interview.py ===")

    content_bank = load_content_bank()
    os.makedirs(DATA_DIR, exist_ok=True)

    theme = sys.argv[1] if len(sys.argv) > 1 else None
    configs = MOCK_INTERVIEWS
    if theme:
        configs = [c for c in configs if c["theme"] == theme]
        if not configs:
            print(f"ERROR: Unknown theme '{theme}'")
            sys.exit(1)

    results = []
    for config in configs:
        print(f"\n--- #{config['id']}: {config['title']} ---")
        result = generate_episode(config, content_bank)
        if result:
            print(f"  MP3: {result['file_size_bytes']/(1024*1024):.1f} MB, {result['duration']}")
            results.append(result)

    print(f"\nDone — {len(results)} mock interview episodes generated")


if __name__ == "__main__":
    main()
