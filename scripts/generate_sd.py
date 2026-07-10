#!/usr/bin/env python3
"""generate_sd.py — Think-aloud system design episodes.

Each episode is a detailed think-aloud walkthrough, exactly like
reasoning through a system design interview in real time.

Voice: en-US-BrianNeural (casual, approachable, sincere)
Duration: 15-20 min per episode (target ~2500 words)
"""

import json, os, sys, subprocess, shutil, tempfile
from datetime import datetime, timezone

from tts import synthesize, get_duration_str

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_BANK_PATH = os.path.join(SCRIPT_DIR, "content_bank.json")
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

THINK_ALOUD_EPISODES = [
    {
        "id": 23, "theme": "sd-fundamentals",
        "title": "SD Fundamentals Think-Aloud",
        "subtitle": "CAP, ACID vs BASE, Consensus",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're working through three fundamental concepts: CAP theorem, ACID versus BASE, and consensus protocols. These come up in almost every system design interview, not as direct questions, but as the vocabulary you need when discussing trade-offs.

I'm going to reason through these out loud, exactly like I would in an actual interview. Listen for how I connect concepts to real systems and name trade-offs explicitly.

Let's start with CAP theorem.

OK, so the question is about CAP theorem. Let me think through this step by step. CAP stands for Consistency, Availability, and Partition tolerance. The theorem says that in a distributed system, you can only guarantee two out of three during a network partition.

Now, here's the key insight that most people miss in interviews. Partition tolerance isn't really a choice. Network partitions WILL happen. It's not a question of if, it's when. Cables get cut, switches fail, data centers lose connectivity. So the real trade-off is between consistency and availability DURING a partition.

Let me work through what that means concretely. If the network splits, do you reject requests to keep data consistent? That's the CP approach. Systems like ZooKeeper and etcd do this. When there's a partition, the minority side refuses to serve requests, because it can't guarantee the data is up to date. You get consistency, but you sacrifice availability for those nodes.

Or do you accept requests and risk inconsistencies? That's AP. Cassandra and DynamoDB in eventually consistent mode do this. Both sides of the partition keep serving, and when the network heals, they reconcile. You get availability, but you might serve stale data.

Hmm, but which one do you pick in an interview? Well, it depends on the system. For a payment system, I'd absolutely go CP. You cannot risk double-charging someone or showing the wrong balance. But for a social media feed? AP is fine. Seeing a post five seconds late is not a crisis.

The important thing to say in an interview is: most real systems aren't strictly CP or AP. DynamoDB lets you tune consistency per request. You can do a strongly consistent read when you need it, and an eventually consistent read when you don't. That's a sophisticated answer that shows you understand the nuance.

OK, moving on. Let's talk about ACID versus BASE.

So ACID stands for Atomicity, Consistency, Isolation, and Durability. These are the guarantees that traditional relational databases give you for transactions. Every transaction is all-or-nothing, isolated from other transactions, and once committed, it's permanent.

BASE stands for Basically Available, Soft state, Eventually consistent. This is the opposite philosophy. You accept that data might be temporarily inconsistent in exchange for better availability and performance.

Now, in an interview, you don't just pick one. The right answer is: use both, for different parts of your system. For financial transactions, account balances, anything involving money, you need ACID. Period. There's no room for eventual consistency when you're transferring funds between accounts. The database must guarantee that either both accounts are updated, or neither is.

But for everything else, like caching user preferences, showing read counts, or precomputing analytics, BASE is totally fine. If the count is off by a few for a minute, nobody cares.

The mistake I see a lot of candidates make is treating this as an either-or decision. In practice, most production systems use ACID for the critical path and BASE for everything else. Stripe uses PostgreSQL for transactions but Redis for caching. That's the real answer.

Let me also mention something about isolation levels, because this comes up in follow-up questions. The I in ACID, isolation, has multiple levels. Read committed is the default in most databases, but it doesn't prevent all anomalies. Serializable is the strongest, but it can hurt performance. In an interview, mentioning that you understand isolation levels and would choose based on the consistency requirements of the specific operation is a strong signal.

Alright, let's talk about consensus protocols.

So consensus is about how distributed nodes agree on a value, even when some nodes fail. This is the foundation of leader election, distributed locking, and replicated state machines.

The most famous consensus protocol is Paxos, but it's notoriously hard to understand and implement. Google spent years getting it right for Chubby. The practical alternative is Raft, which was specifically designed to be understandable. Raft separates the problem into leader election and log replication, and it's used by etcd, CockroachDB, and Consul.

Here's how Raft works at a high level. One node is the leader. All writes go through the leader. The leader replicates its log to followers. A write is committed once a majority of nodes acknowledge it. If the leader fails, the remaining nodes hold an election. The node with the most up-to-date log becomes the new leader.

The key number to remember is the quorum size. For N nodes, you need N divided by 2, plus 1, to agree. So with 5 nodes, you need 3. With 3 nodes, you need 2. This means the system can tolerate N minus 1 over 2 failures. With 5 nodes, 2 can fail and the system still works.

There's also Byzantine Fault Tolerance, which handles malicious nodes, not just crashed ones. This is what blockchain systems use. But for most enterprise systems, you don't need BFT because you control all the nodes. It's much more expensive, requiring more rounds of communication.

In an interview, the key thing to say about consensus is: it's the mechanism that makes distributed databases consistent. Without consensus, you can't have a single-leader database that survives leader failure. And if you're designing a system that needs strong consistency, you should mention that you'd use a consensus protocol for leader election and replication.

So... let me quickly review what we covered today.

For CAP theorem, the core trade-off is between consistency and availability during a partition. The sophisticated answer is that most systems offer tunable consistency, not strictly CP or AP.

For ACID versus BASE, the key insight is that you use both. ACID for the critical path, BASE for everything else. Don't treat it as either-or.

For consensus protocols, remember that Raft is the practical choice, the quorum formula is N over 2 plus 1, and consensus is what makes strongly consistent distributed databases possible.

Remember, in a system design interview, these fundamentals come up as part of your design discussion, not as standalone questions. The interviewer wants to see you naturally reference them when explaining your choices. That's what we practiced today.

Great work. Keep practicing out loud. See you next time."""
    },
    {
        "id": 24, "theme": "sd-infrastructure",
        "title": "Infrastructure Think-Aloud",
        "subtitle": "Load Balancing, Caching, CDN, Message Queues",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're working through four infrastructure building blocks: load balancing, caching, content delivery networks, and message queues. These are the components you'll reference in almost every system design interview.

Let me reason through each one out loud, focusing on the trade-offs and when to pick which option.

Let's start with load balancing.

OK, so load balancing is about distributing incoming traffic across multiple servers. The first question I'd ask in an interview is: what layer are we load balancing at? Layer 4 or Layer 7?

Layer 4 load balancing operates at the transport level. It looks at the IP address and port number and forwards the connection. It's fast because it doesn't inspect the packet content. But it can't make smart routing decisions. It can't route based on the URL path, or the HTTP headers, or the cookie.

Layer 7 load balancing operates at the application level. It can inspect the HTTP request and route based on the URL, headers, cookies, or any application-level information. This is much more flexible but adds some latency because the load balancer has to parse the request.

In practice, most modern systems use Layer 7. The latency overhead is minimal compared to the routing flexibility. AWS ALB, NGINX, HAProxy, these are all Layer 7 load balancers.

Now, what about the routing algorithm? Round robin is the simplest. Each request goes to the next server in order. But it doesn't account for server capacity or current load. Least connections is better. It sends each request to the server with the fewest active connections, which naturally balances load across servers with different capacities.

Then there's consistent hashing, which I'd use when I need session affinity. This means the same user always goes to the same server. This is important for stateful applications where the server has in-memory session data. With consistent hashing, when a server is added or removed, only a fraction of the keys need to be remapped.

The trade-off here is: session affinity gives you stateful behavior, but it limits your ability to distribute load evenly. If one user generates way more traffic than others, their assigned server becomes a hotspot.

Alright, let's talk about caching.

Caching is probably the single most impactful performance optimization in any system. If I can only make one change to improve performance, I'd add a cache.

The main caching strategies are cache-aside, read-through, write-through, and write-behind. Let me think through when to use each.

Cache-aside is the most common. The application checks the cache first. On a miss, it loads from the database and writes to the cache. The cache doesn't know about the database. It's simple, and it works well when the application has a clear read-write pattern. The downside is that the application has to manage the cache explicitly.

Read-through is similar to cache-aside, but the cache layer automatically loads from the database on a miss. The application only talks to the cache. This simplifies the application code but means the cache layer has to understand the database schema.

Write-through means writes go to the cache and the database simultaneously. The cache always has the latest data. But writes are slower because you have to update both. This is good when you have a high read-to-write ratio.

Write-behind means writes go to the cache first and are asynchronously flushed to the database. Writes are fast, but there's a risk of data loss if the cache fails before the data is flushed. I'd only use this for data that can be reconstructed or where occasional loss is acceptable.

For eviction policies, LRU, or least recently used, is the most common and works well for most workloads. TTL, or time to live, is essential for data that becomes stale. In a system design interview, I'd mention both and explain that I'd use LRU for capacity management and TTL for data freshness.

Now, let's talk about CDNs.

A CDN, or content delivery network, distributes your content from servers that are geographically close to your users. The goal is to reduce latency. If your origin server is in Virginia and your user is in Tokyo, the round trip time is about 150 milliseconds. With a CDN, the content is served from a server in Tokyo, and the latency drops to maybe 10 milliseconds.

CDNs work best for static content like images, JavaScript, CSS, and video. These files don't change often and can be cached for long periods. A typical setup is to put static assets on a CDN with a 1-year cache TTL and use content hashing in the filename for cache busting when the file changes.

For dynamic content, CDNs are trickier. You need short TTLs, and the cache hit rate is lower. But even for dynamic content, CDNs can help by terminating TLS connections closer to the user and by using techniques like stale-while-revalidate, where the CDN serves the stale content while fetching fresh content in the background.

Edge computing takes this further by running your code at the CDN edge. Cloudflare Workers, AWS Lambda at Edge. This lets you do personalization, A/B testing, and request routing without the round trip to your origin. In an interview, mentioning edge computing shows you're thinking about the latest architectural patterns.

OK, last one: message queues.

Message queues decouple producers from consumers. Instead of service A calling service B directly, service A publishes a message to a queue, and service B processes it asynchronously. This gives you three benefits. First, if service B is down, the messages pile up in the queue and get processed when it comes back. Second, if service B is slow, the queue absorbs the load and prevents it from propagating upstream. Third, you can add more consumers to handle higher throughput without changing the producer.

The key design choice with message queues is the delivery guarantee. At-most-once means a message might be lost. Fastest, but lowest guarantee. At-least-once means a message is never lost, but it might be delivered twice. This requires consumers to be idempotent. Exactly-once is the gold standard but very hard to achieve. In practice, most systems use at-least-once with idempotent consumers to simulate exactly-once.

For ordering, Kafka gives you FIFO ordering within a partition, but no guaranteed order across partitions. If you need strict ordering, you need all related messages in the same partition, which limits parallelism. This is a fundamental trade-off: ordering versus parallelism.

In an interview, I'd mention that for a payment system, I'd use at-least-once delivery with idempotent consumers and idempotency keys. For a logging or analytics system, at-most-once is fine because losing a few events doesn't matter.

So... let me quickly review. For load balancing, remember Layer 4 versus Layer 7 and consistent hashing for session affinity. For caching, know the four strategies and when to use each. For CDN, focus on static content with long TTLs and edge computing for dynamic personalization. For message queues, the key trade-off is delivery guarantee versus performance, and ordering versus parallelism.

Great work today. See you next time."""
    },
    {
        "id": 25, "theme": "sd-data",
        "title": "Data Architecture Think-Aloud",
        "subtitle": "Sharding, Replication, Partitioning",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're working through data architecture: sharding, replication, and consistent hashing. These are the techniques you use when your data is too big for a single machine, which in an interview, it almost always is.

Let me reason through each one, focusing on the trade-offs and the failure scenarios.

Let's start with database sharding.

So, sharding is about horizontally partitioning your data across multiple database instances. Each shard holds a subset of the data. The question is: how do you decide which data goes on which shard?

There are three main sharding strategies. Hash-based sharding takes a key, like user ID, hashes it, and uses the hash to determine the shard. This gives you even distribution, which is great. But resharding is expensive. If you add a new shard, you need to move a lot of data. In practice, you'd use consistent hashing to minimize the data movement when resharding.

Range-based sharding assigns key ranges to shards. Users with IDs 1 through a million go on shard 1, a million and 1 through 2 million on shard 2, and so on. This supports range queries, which hash sharding doesn't. But it can create hotspots. If you have a popular user whose ID falls in one range, that shard gets disproportionately loaded.

Directory-based sharding uses a lookup table that maps each key to a shard. This is the most flexible because you can move keys between shards without rehashing. But the lookup table itself becomes a bottleneck and a single point of failure.

In an interview, I'd start with hash-based sharding for even distribution, and mention that I'd use consistent hashing to make resharding manageable. If the interviewer asks about range queries, I'd discuss range-based sharding and the hotspot problem.

Now, the hardest operational problem with sharding is resharding. When you add a shard, you need to move data from existing shards to the new one, without downtime. The standard approach is dual-write: write to both the old and new shard layout during the migration, then switch reads to the new layout, then stop writing to the old layout. This is complex and error-prone, but it's the state of the art.

Another issue is cross-shard queries. If you need to join data from two shards, you have to do it in the application layer. This is slow and defeats the purpose of sharding. In an interview, you should explicitly say that you'd design your shard key to avoid cross-shard queries. For a social media app, shard by user ID so that all of a user's data, their posts, followers, and messages, are on the same shard.

Alright, let's talk about replication.

Replication is about copying data across multiple servers for redundancy, availability, and read scalability. There are three main topologies.

Single-leader replication has one write node and multiple read replicas. All writes go to the leader and are replicated to the followers. This is the simplest model and gives you strong consistency if you use synchronous replication. But the leader is a write bottleneck, and if the leader fails, you need to promote a follower, which takes time.

Multi-leader replication has multiple write nodes. This gives you higher write availability, which is useful in multi-region setups where writes happen in different data centers. But you need conflict resolution. If two leaders accept writes to the same row simultaneously, which one wins? The common approaches are last-write-wins using timestamps, or application-level conflict resolution. Both have trade-offs.

Leaderless replication lets any node accept writes. This gives you the highest availability. Cassandra and DynamoDB use this model. But consistency is eventual. If two nodes accept conflicting writes, you need a reconciliation strategy, like DynamoDB's read-repair and anti-entropy using Merkle trees.

In an interview, I'd say that for most systems, single-leader replication is the right default. It's simple and gives you strong consistency. I'd only go to multi-leader for multi-region write requirements, and leaderless for systems where availability is more important than consistency.

One important concept to mention is read-after-write consistency. After a user writes something, they should be able to read it back immediately, even if the read goes to a replica that hasn't received the replication yet. The standard solution is to route the user's reads to the leader for a short window after their write.

OK, last one: consistent hashing.

Consistent hashing is the algorithm that makes distributed caches and databases scalable without massive data movement when nodes are added or removed.

Here's how it works. Imagine a circle with points from 0 to 2 to the power of 32 minus 1. Both nodes and keys are placed on this circle by hashing their identifiers. Each key belongs to the nearest node clockwise on the circle.

When a node joins, it takes over the keys between it and its predecessor. Only those keys need to move. When a node leaves, its keys move to the next node clockwise. This means adding or removing a node only affects K divided by N keys, where K is the total number of keys and N is the total number of nodes. This is much better than traditional hashing, where adding a node would require remapping nearly all keys.

Virtual nodes make this even better. Instead of mapping each physical node to one point on the circle, you map it to many points. This gives a more even distribution of keys across nodes, even if some nodes have more capacity than others.

DynamoDB and Cassandra both use consistent hashing with virtual nodes. It's the standard approach for any distributed key-value store.

In an interview, I'd explain the algorithm briefly, then focus on the practical implications. Consistent hashing gives us minimal data movement when scaling, but it can create hotspots if some keys are much more popular than others. For hot keys, you'd need a caching layer in front of the database.

So... let me review. For sharding, use hash-based with consistent hashing, and design your shard key to avoid cross-shard queries. For replication, single-leader is the default, go multi-leader for multi-region writes, leaderless for maximum availability. For consistent hashing, remember the ring model, virtual nodes for even distribution, and that it solves the resharding problem.

Great work today. See you next time."""
    },
    {
        "id": 26, "theme": "sd-api-microservices",
        "title": "API & Microservices Think-Aloud",
        "subtitle": "API Design, Microservices Architecture",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're working through API design and microservices architecture. These come up in almost every system design interview because they define how your system's components communicate and how you decompose a large system into manageable pieces.

Let's start with API design.

So, the three main API styles are REST, gRPC, and GraphQL. Let me think through when to use each.

REST is the default choice. It's resource-oriented, uses HTTP verbs, and is stateless. GET to read, POST to create, PUT to update, DELETE to remove. It's simple, widely understood, and works everywhere. The downside is that it can require many round trips. If a mobile app needs to load a user profile with their posts and comments, that might be three separate REST calls. This is the over-fetching and under-fetching problem.

gRPC uses protocol buffers and HTTP/2 for binary, high-performance communication. It's fast because the payloads are smaller and the serialization is efficient. It supports bidirectional streaming, which is great for real-time communication between services. The downsides are that it's harder to debug because the payloads are binary, browser support is limited, and you need code generation for each language. In practice, gRPC is great for internal service-to-service communication, but you'd typically expose REST externally and use a gateway to translate.

GraphQL lets the client specify exactly what data it needs. No over-fetching, no under-fetching. One query gets exactly the data the UI needs. The downside is complexity on the server side. You need a resolver for each field, there's a risk of N-plus-one queries, and caching is more complex because each query is different.

In an interview, I'd say: REST for external APIs, gRPC for internal service-to-service communication, and GraphQL only if you have a real need for flexible client-driven queries. Don't pick GraphQL just because it's trendy.

Now, versioning. APIs evolve, and you need a strategy for making changes without breaking existing clients. The three approaches are URL path versioning like slash v1 slash resource, header-based versioning using a custom header like Accept version 1, and query parameter versioning like ?v=1.

URL path versioning is the most common and the easiest to understand. Stripe uses header-based versioning, which is more elegant but requires clients to set headers correctly. The key principle is: add fields as optional, never remove or rename fields. Consumers should ignore unknown fields. This is backward compatibility.

Alright, let's talk about microservices.

So, microservices architecture decomposes a monolith into independently deployable services, each owning a business capability. The key principle is that each service owns its data. No shared databases. This gives you independent deployment, independent scaling, and team autonomy.

But the complexity cost is significant. You need service discovery, so services can find each other. You need an API gateway as the single entry point for clients. You need circuit breakers to stop cascading failures. You need distributed tracing to debug requests that span multiple services. And you need the saga pattern for distributed transactions.

Let me think about when microservices actually make sense. The honest answer is: not for most startups. If you have 5 engineers, a monolith is simpler, faster, and more productive. Microservices make sense when you have 50 or 500 engineers and deployment becomes a bottleneck. Amazon's two-pizza team model works because each team owns their service end-to-end.

The biggest mistake I see in interviews is over-engineering with microservices from the start. A good answer is: start with a monolith, extract services when you have a clear reason. Maybe the payment service needs different scaling than the user service. Maybe the recommendation engine is deployed more frequently. Extract services based on data, not assumptions.

The API gateway is worth discussing in detail. It handles authentication, rate limiting, request routing, and protocol translation. All client requests go through the gateway, which routes them to the appropriate service. This means each service doesn't need to implement auth or rate limiting independently. The gateway centralizes these cross-cutting concerns.

But the gateway can become a bottleneck if it does too much. Keep it thin. Routing, auth, rate limiting. Business logic stays in the services.

For service-to-service communication, I'd use asynchronous messaging for operations that don't need immediate consistency, and synchronous REST or gRPC for operations that do. The payment service needs synchronous communication with the ledger service. But sending a confirmation email can be asynchronous via a message queue.

Circuit breakers are essential in a microservices architecture. If service A calls service B, and service B is failing, service A should stop calling it after a few failures. This is the circuit breaker pattern. Open the circuit, return a fallback response, and try again after a timeout. This prevents cascading failures where one slow service takes down everything upstream.

So... let me review. For API design, REST externally, gRPC internally, version via URL path. For microservices, start with a monolith, extract services based on data not assumptions. Each service owns its data. Use an API gateway for cross-cutting concerns. Use circuit breakers to prevent cascading failures. And use asynchronous messaging for operations that don't need immediate consistency.

Great work today. See you next time."""
    },
    {
        "id": 27, "theme": "sd-reliability",
        "title": "Reliability Think-Aloud",
        "subtitle": "Idempotency, Rate Limiting, Observability",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're working through three reliability topics: idempotency, rate limiting, and observability. These are what separate systems that work in demos from systems that work in production.

Let me reason through each one, focusing on the failure scenarios and how to handle them.

Let's start with idempotency.

So, an operation is idempotent if executing it multiple times has the same effect as executing it once. This sounds abstract, but it's critical in distributed systems where retries are inevitable.

Here's the scenario. A client sends a payment request. The server processes it. The client doesn't get a response because of a network timeout. Did the payment go through or not? The client doesn't know. So it retries. Without idempotency, the payment gets processed twice. Double charge. That's a real incident, not a theoretical concern.

The solution is the idempotency key. The client generates a unique key for each operation and sends it with the request. The server stores the key and the result. If the same key comes in again, the server returns the stored result without reprocessing. Stripe does this really well. Every API call requires an Idempotency-Key header.

In an interview, I'd walk through the implementation. The idempotency key goes in the database with a unique constraint. When a request comes in, check if the key exists. If it does, return the previous result. If it doesn't, process and store. This adds latency and storage, but the cost of not doing it is double-charges and duplicate messages.

Some operations are naturally idempotent. PUT replaces the entire resource, so calling it twice gives the same result. DELETE is idempotent because deleting something that's already deleted is the same as deleting it once. POST is NOT naturally idempotent because each call creates a new resource. That's why POST is the one that needs the idempotency key.

Alright, let's talk about rate limiting.

Rate limiting controls how many requests a client can make in a given time period. It protects your service from being overwhelmed, whether by a malicious attacker or by a buggy client that's sending too many requests.

There are four main algorithms. Token bucket is the most common. Tokens are added to the bucket at a fixed rate. Each request consumes a token. If the bucket is empty, the request is rejected. The bucket has a maximum capacity, which allows controlled bursts. This is what Stripe and GitHub use.

Leaky bucket processes requests at a fixed rate, like water dripping from a bucket. Excess requests are queued or rejected. This smooths traffic but doesn't allow any bursts.

Fixed window counts requests in a fixed time window, like one minute. Simple, but it allows a burst at the boundary. If the limit is 100 per minute, a client could send 100 requests at 11:59:59 and another 100 at 12:00:01. That's 200 requests in two seconds.

Sliding window is the most accurate. It counts requests in a rolling time window. But it uses more memory because you need to store the timestamp of each request.

In an interview, I'd say: use token bucket for most cases because it allows controlled bursts while enforcing the average rate. Use sliding window if you need precise enforcement. And always return rate limit headers, X-RateLimit-Limit, X-RateLimit-Remaining, and X-RateLimit-Reset, so clients can adapt.

For distributed rate limiting, you need a shared counter. Redis with atomic increment works well. Each request increments the counter, and if it exceeds the limit, the request is rejected. The challenge is that this adds a Redis round trip to every request, adding latency. Some systems use a local rate limiter as a first check and a distributed limiter as a second check to reduce the Redis load.

Now, let's talk about observability.

Observability is the ability to understand the internal state of a system from its external outputs. It's not just monitoring, which is about known-knowns. Observability is about asking questions you didn't think to ask in advance.

The three pillars are metrics, logs, and traces.

Metrics are numeric time-series data. Request rate, error rate, latency percentiles. The RED method is useful here: Rate, Errors, Duration. For every service, track these three. Prometheus and Grafana are the standard tools for metrics.

Logs are discrete events with context. Structured JSON logs with a request ID, user ID, timestamp, and event type. The key is correlation IDs. Attach a unique ID to each request and propagate it across all services. Then you can search logs by correlation ID and see the full journey of a request. ELK stack, or Elasticsearch, Logstash, Kibana, is the classic log aggregation system.

Traces show the end-to-end flow of a request across services. Each service contributes a span, which is a unit of work with a start time, end time, and metadata. Traces are essential for debugging latency issues in microservices. If a request takes 5 seconds and it goes through 8 services, the trace tells you which service is slow. Jaeger and Zipkin are the standard tracing tools.

In an interview, I'd mention the OpenTelemetry standard, which provides a unified instrumentation layer for all three pillars. Instead of instrumenting each tool separately, you instrument once with OpenTelemetry and export to any backend.

For alerting, I'd use SLO-based alerting rather than threshold-based. Define your service level objectives, like p99 latency under 200 milliseconds, and alert on the burn rate. If you're burning through your error budget too fast, page the on-call engineer. This is better than alerting on raw thresholds because it accounts for the business impact.

So... let me review. For idempotency, use idempotency keys with unique constraints. For rate limiting, token bucket for most cases, return rate limit headers. For observability, the three pillars are metrics, logs, and traces, use OpenTelemetry for instrumentation, and alert on SLO burn rate.

Great work today. See you next time."""
    },
    {
        "id": 28, "theme": "sd-classic-1",
        "title": "URL Shortener Think-Aloud",
        "subtitle": "Full walkthrough with estimation",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're doing a full walkthrough of a classic interview problem: design a URL shortener like Bitly.

I'm going to work through this exactly like I would in an interview. Clarify requirements, estimate scale, design the high-level architecture, dive deep into the key component, and name the trade-offs.

Let's get started.

So the problem is: design a URL shortener. The first thing I'd do is clarify the requirements.

What are the functional requirements? Given a long URL, generate a short unique alias. Given a short alias, redirect to the original long URL. Optionally, track analytics: how many clicks, where they come from, when they happen.

What are the non-functional requirements? High availability for reads, because redirects need to work. Low latency for redirects, ideally under 50 milliseconds. Durability, once a mapping is created, it should never be lost.

Now let me estimate the scale. Let's say we're handling 100 million URLs per day. The read-to-write ratio is about 10 to 1, so that's a billion reads per day. For daily writes, 100 million divided by 86,400 seconds is about 1,200 writes per second. With a 2x peak multiplier, that's 2,400 write QPS. For reads, 10 times that, so 12,000 read QPS average, 24,000 at peak.

For storage, let's say we have 10 billion total URLs. Each entry is about 200 bytes: the short code, the long URL, metadata like creation date and user ID. So 10 billion times 200 bytes is about 2 terabytes. Very manageable.

OK, so what's the API? Two main endpoints. POST slash shorten, takes a long URL and returns a short code. GET slash short code, looks up the long URL and returns a 301 or 302 redirect.

Now, 301 versus 302. This is a detail that interviewers love to ask about. 301 is a permanent redirect. The browser caches it. Subsequent requests for the same short URL go directly to the long URL without hitting our server. This is faster for the user but means we can't track clicks. 302 is a temporary redirect. The browser always hits our server first. This is slower for the user but lets us track every click. I'd use 302 by default and offer 301 as an option for users who don't need analytics.

Now let me think about the ID generation. This is the hardest part of the design.

We need to generate short, unique codes. A 7-character code using base 62, that's 62 to the 7th power, which is about 3.5 trillion possible codes. That's more than enough for 10 billion URLs.

The simplest approach is an auto-incrementing counter. Each new URL gets the next counter value, which is encoded in base 62. The problem is that this creates a single point of failure and a bottleneck. You need a distributed, atomically incrementing counter.

A better approach is to pre-generate a pool of random keys. A separate service generates a batch of, say, 10,000 random 7-character strings, checks that they're not already in the database, and stores them in a key pool. When the application needs a new short code, it takes one from the pool. When the pool runs low, it generates another batch. This avoids the single-point-of-failure problem and is very fast because the key is already generated.

For the data store, this is a simple key-value lookup. Short code to long URL. A NoSQL store like DynamoDB or Cassandra is perfect. Hash-based sharding by short code gives us even distribution. With 2 terabytes of data, we could fit it on a single machine, but for availability and throughput, we'd shard across multiple nodes.

For reads, caching is essential. With a 10 to 1 read-to-write ratio, a cache-aside pattern with Redis would absorb most of the read traffic. The cache hit rate would be very high because popular URLs are accessed much more frequently than unpopular ones. This follows the Zipf distribution.

Now let me think about the redirect flow. A user clicks a short link. The request hits our load balancer, which routes it to a web server. The web server checks the Redis cache. If the long URL is in the cache, it returns a 302 redirect immediately. Cache hit latency is under 5 milliseconds. If it's a miss, the server queries the database, writes the result to the cache, and returns the redirect. Cache miss latency is maybe 20 to 50 milliseconds.

For analytics, I'd use an asynchronous pipeline. When a redirect happens, the web server publishes an event to a message queue like Kafka. A separate analytics consumer reads from the queue, aggregates the data by time, geography, and referrer, and writes the results to a data warehouse. This keeps the redirect path fast because analytics processing is decoupled.

So... let me think about what could go wrong. The failure mode I'm most concerned about is a cache stampede. If a popular URL's cache entry expires and thousands of requests hit the database simultaneously, it could overwhelm the database. The mitigation is request coalescing, where only one request goes to the database and the rest wait for its result. Another option is to use a long TTL with background refresh, so the cache never actually expires for popular URLs.

Another concern is the key generation service. If it goes down, we can't create new short URLs. To mitigate, I'd keep a large pool of pre-generated keys on each application server, so we can survive a key generation outage for hours.

So... let me summarize the key trade-offs. 301 versus 302: permanent redirect is faster but loses analytics. Counter versus pre-generated keys: counter is simpler but creates a bottleneck. Pre-generated keys are more complex but more scalable. Cache-aside with Redis: high hit rate for popular URLs, but need stampede protection.

Remember, in a URL shortener interview, the interesting parts are the ID generation strategy and the caching strategy. Get those right and you'll impress the interviewer.

Great work today. See you next time."""
    },
    {
        "id": 29, "theme": "sd-classic-2",
        "title": "Chat System Think-Aloud",
        "subtitle": "Real-time messaging, WebSocket vs polling",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're working through another classic: design a chat system like WhatsApp or Slack.

Let me work through this step by step, exactly like in an interview.

So, the problem is: design a real-time messaging system. First, let me clarify the requirements. We need to support one-on-one chats and group chats. Users need to see when their contacts are online. Messages should be stored so you can see history when you log back in. And we need to handle push notifications for when the app is in the background.

Now, let me estimate the scale. Let's say 50 million daily active users. Each user sends maybe 20 messages per day, so that's a billion messages per day. At peak, maybe 10,000 messages per second. Messages are stored forever, so with an average message size of 100 bytes, that's about 50 terabytes per year.

OK, so the first big design decision is: how do we deliver messages in real-time? There are three options.

Polling is the simplest. The client periodically asks the server for new messages. Easy to implement, but wasteful. If the client polls every 5 seconds and there are no messages, that's wasted bandwidth and server resources. And 5 seconds is too slow for a chat app. People expect near-instant delivery.

Long polling is better. The client sends a request, and the server holds the connection open until there's a new message or until a timeout. This reduces wasted requests but still has overhead from repeatedly establishing new connections.

WebSocket is the best option for real-time chat. It's a persistent, bidirectional connection between the client and server. Once established, both sides can send messages at any time without the overhead of HTTP request-response cycles. This is what WhatsApp, Slack, and most modern chat apps use.

So I'd go with WebSocket for message delivery. The server maintains a mapping of user ID to WebSocket connection. When a message arrives for a user, the server looks up their connection and pushes the message.

Now, here's the challenge. With 50 million daily active users, you can't have all WebSocket connections on one server. You need connection servers that handle the WebSocket connections, distributed across many machines. A single server can handle maybe 50,000 to 100,000 concurrent connections. So you need 500 to 1,000 connection servers.

When user A sends a message to user B, how does it get to user B's connection server? You need a routing layer. One approach is to have a message queue. User A's connection server publishes the message to a topic for user B. User B's connection server is subscribed to that topic and receives the message.

For group chats, this gets more complex. When someone sends a message to a group of 100 people, you need to fan it out to all 100 connections. There are two strategies: fan-out on write, where you create 100 copies of the message, one for each recipient, or fan-out on read, where you store one copy and each recipient queries it.

For a chat system, fan-out on write is usually better because reads need to be fast. When you open a chat, you want to see messages instantly, not wait for a database query. So we write one copy per recipient's inbox. For a group of 100, that's 100 writes, which is a lot. But it makes reads O(1) because you just query your own inbox.

For the database, I'd use a message table partitioned by conversation ID. Each conversation, whether one-on-one or group, has its own partition. This avoids cross-partition queries and keeps the data model simple.

For presence, the online status indicator, I'd use a heartbeat mechanism. Each client sends a heartbeat every 30 seconds via their WebSocket connection. The server stores the user's online status in Redis with a TTL. When the TTL expires, the user is considered offline. Status changes are published to the user's contacts via the same WebSocket mechanism.

For offline users, messages need to be stored and delivered when they come back online. The simplest approach is to store all messages in the database and let the client pull missed messages when it reconnects. The client tracks the last message ID it received, and on reconnect, it queries for all messages after that ID.

For push notifications, when a message is for an offline user and they don't have the app open, we send a push notification via Apple Push Notification Service or Firebase Cloud Messaging. The server detects that the user is offline and triggers the push notification through a notification service.

So... what are the bottlenecks? WebSocket connection management at scale. With 50 million users, maintaining millions of concurrent WebSocket connections requires significant infrastructure. Fan-out for large groups. A group with 10,000 members means 10,000 writes per message. And message ordering. In a group chat, messages must appear in order for all members. Using a single partition per conversation, with sequential IDs, gives us ordering within that conversation.

The trade-off I'd highlight in an interview is between fan-out on write and fan-out on read. Fan-out on write is faster for reads but more expensive for writes and storage. For most chat apps with typical group sizes under 200, fan-out on write is the right choice. But for something like a Discord server with 10,000 members, you might need a hybrid approach.

Great work today. See you next time."""
    },
    {
        "id": 30, "theme": "sd-classic-3",
        "title": "News Feed Think-Aloud",
        "subtitle": "Fan-out, caching, ranking",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're working through design a news feed, the Instagram or Twitter problem. This is one of the most common system design interview questions because it touches on so many concepts: fan-out strategies, caching, ranking, and real-time updates.

Let me work through this step by step.

So, the problem is: generate a personalized feed of posts from people you follow. Users can post, follow other users, and scroll through their feed. The feed should be ranked, not just chronological, and it should load fast.

Let me estimate the scale. 100 million daily active users. 500 million posts per day. Average user follows 200 people. Each feed page shows 20 posts.

Now, the core design question is: how do you generate a user's feed? There are two fundamental approaches.

Fan-out on write means that when a user posts, you push that post to the feed of every one of their followers. If they have 200 followers, you write 200 copies. This makes reads very fast because the feed is pre-computed. When a user opens the app, you just read their feed from the cache. O(1) read time. But writes are expensive, especially for popular users with millions of followers. When a celebrity posts, you need to push to millions of feeds. That's a huge write operation.

Fan-out on read means that when a user requests their feed, you query the posts of everyone they follow and merge them. Reads are slower because you need to query 200 users' posts and sort them. But writes are O(1). You just store the post once.

The standard approach, which I'd present in an interview, is a hybrid. Fan-out on write for most users, who have a manageable number of followers. Fan-out on read for celebrities with millions of followers. When a celebrity posts, you don't push to millions of feeds. Instead, when a regular user's feed is generated, you check for recent posts from celebrities they follow and merge them in.

This is the approach Instagram uses. They have a pre-computed feed for each user that includes posts from regular follows. For celebrity follows, they query the celebrity's recent posts at read time and merge them into the feed.

Now, for the data model. I'd have a users table, a follows table, a posts table, and a feed table. The feed table is the pre-computed feed for each user. Each row is a user ID, a post ID, and a timestamp. When a user posts, their post is inserted into the feed table of each follower.

For caching, the feed table would be cached in Redis. When a user opens the app, the first page of their feed is served from Redis. If they scroll further, we query the database for the next page. Pagination should be cursor-based, not offset-based. Offset-based pagination is slow and inconsistent because new posts arrive while the user is scrolling. With cursor-based pagination, you use the timestamp or ID of the last post as the cursor, and get posts after that cursor.

For ranking, the simplest approach is reverse chronological order. Most recent posts first. This is what Twitter used to do. But modern feeds use ranking algorithms that consider engagement, recency, and relevance. A post from someone you interact with frequently should rank higher than a post from someone you rarely engage with.

In an interview, I'd say: start with reverse chronological, then mention that you could add ranking based on engagement signals like likes, comments, and time spent viewing. The ranking model would be a machine learning model trained on user engagement data. Pre-computed rankings for the top of the feed, and fallback to chronological for older posts.

For real-time updates, when a new post arrives while the user is looking at their feed, you need to show it without a full page refresh. The approach is to push new post IDs to the client via WebSocket or server-sent events. When a new post arrives for a user, the feed service publishes it to a WebSocket channel that the client is subscribed to. The client receives the post ID, fetches the post content, and inserts it at the top of the feed.

So... what are the bottlenecks? Fan-out for popular users. Even with the hybrid approach, a user with a million followers who posts 10 times a day generates 10 million feed writes per day. Caching the entire feed for 100 million users in Redis would require significant memory. And ranking computation needs to happen quickly so the feed loads fast.

The key trade-off to name in an interview is: pre-computed feeds give O(1) read time but expensive writes, especially for popular users. The hybrid approach mitigates this but adds complexity. And ranking adds user engagement but increases computation cost.

Great work today. See you next time."""
    },
    {
        "id": 31, "theme": "sd-fintech-payment",
        "title": "Payment System Think-Aloud",
        "subtitle": "Fintech: idempotency, double-charge, reconciliation",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're designing a payment system, which is one of the most important fintech system design questions. If you're interviewing for a fintech company, this WILL come up.

I'm going to work through this as if I'm in an actual interview, focusing on the things that make payment systems different from other systems: financial correctness, idempotency, reconciliation, and regulatory compliance.

Let's start by clarifying the requirements. A payment system needs to accept a payment from a customer, authorize it with the payment network or bank, capture the funds, and settle them into the merchant's account. It needs to handle failures gracefully, which in payments means never losing money and never double-charging.

Let me estimate the scale. Say we're processing for a million businesses, each doing about 1,000 transactions per day on average. That's a billion transactions per day. At peak, with a 3x multiplier for events like Black Friday, that's about 35,000 transactions per second. Each transaction record is about 500 bytes, so that's 500 gigabytes per day, and with 7-year retention for compliance, about 1.3 petabytes total.

Now, the API. The core endpoint is POST slash payments. It takes an amount, a currency, a payment method like a credit card token, and critically, an idempotency key. The idempotency key is the single most important concept in payment system design. Let me explain why.

When a client sends a payment request, three things can happen. One, the request succeeds and the client gets a response. Two, the request fails and the client gets an error. Three, the request succeeds on the server, but the client doesn't get the response because of a network timeout. In case three, the client doesn't know if the payment went through. So it retries. Without idempotency, the payment gets processed twice. Double charge. That's a serious incident.

The idempotency key solves this. The client generates a unique key, like a UUID, for each payment attempt. The server stores this key in the database with a unique constraint. When a request comes in, the server first checks if the idempotency key already exists. If it does, it returns the previous result without reprocessing. If it doesn't, it processes the payment and stores the key with the result.

This sounds simple, but the implementation has subtleties. The check and the processing need to be atomic. You can't check for the key, then process, then store, because between check and store, another request with the same key could slip through. The solution is to use a database transaction: insert the idempotency key first with a pending status, process the payment, then update the key with the result. If the insert fails because the key already exists, return the existing result.

Now let me think about the payment state machine. A payment goes through several states. It starts as pending when the request is received. Then it becomes authorized when the bank confirms the funds are available. Then captured when the funds are actually transferred. If something goes wrong, it becomes failed. After capture, it can be refunded, which returns the money to the customer. Or disputed, which is when the customer challenges the charge through their bank.

Each state transition needs to be recorded in the ledger. The ledger is an append-only, double-entry accounting system. Every financial movement is recorded as a pair of entries: a debit and a credit that must balance. This is non-negotiable for a payment system. If you process a hundred-dollar payment, the ledger records a hundred-dollar debit from the customer's account and a hundred-dollar credit to the merchant's account.

The ledger must be append-only. You never update or delete entries. If you need to correct an error, you create a reversing entry. This gives you a complete audit trail, which is required for financial regulations.

Now, reconciliation. This is something that most candidates don't mention, and it's critical. Your internal ledger and the bank's records must agree. Every day, you compare your transaction records with the bank's settlement report. If there are discrepancies, you need to investigate and resolve them. This is reconciliation.

Discrepancies can happen for several reasons. A payment was captured on your side but the bank rejected it. A refund was processed on your side but the bank hasn't executed it yet. A chargeback was initiated by the customer's bank without your knowledge. Reconciliation catches all of these.

I'd implement reconciliation as a daily batch job that compares the internal ledger with the bank's statement. Any discrepancies are flagged for manual review. This is operational work, not something you can fully automate, but you can automate the detection.

For the database, I'd use PostgreSQL for the transactional data. ACID compliance is non-negotiable for financial data. I'd shard by merchant ID for horizontal scaling. The ledger would be in a separate database, also PostgreSQL, with append-only tables and no delete permissions.

For the architecture, the payment service receives the request, validates the idempotency key, and creates a pending transaction in the database. It then calls the payment provider's API, like Stripe or Adyen, to authorize the payment. If authorization succeeds, it updates the transaction to authorized and publishes an event to a message queue. The settlement service consumes these events and handles the async settlement with the bank. The ledger service records every financial movement.

This separation of concerns is important. The payment service handles the synchronous flow: receive request, authorize, respond. The settlement service handles the asynchronous flow: capture funds, settle with the bank. The ledger service records everything. Each can fail independently without corrupting the financial data.

For compliance, payment systems must comply with PCI DSS, which means you cannot store raw credit card numbers. You must use tokenization. The payment provider stores the actual card number and gives you a token. You store the token. This way, even if your database is compromised, the attacker doesn't get card numbers.

So... let me summarize the key takeaways for a payment system interview. Idempotency keys with unique constraints prevent double charges. The payment state machine tracks every transition. The ledger is append-only, double-entry, and ACID compliant. Reconciliation catches discrepancies between your records and the bank's. And PCI DSS compliance requires tokenization, never storing raw card numbers.

If you can cover all five of these areas in an interview, you'll stand out from most candidates who only talk about the high-level architecture.

Great work today. See you next time."""
    },
    {
        "id": 32, "theme": "sd-fintech-ledger",
        "title": "Ledger System Think-Aloud",
        "subtitle": "Fintech: double-entry, append-only, ACID, audit",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're designing a ledger system, the double-entry accounting system that records every financial transaction. This is the source of truth for account balances in any fintech company.

Let me reason through this step by step.

So, what is a ledger? At its core, a ledger records every financial movement as a pair of entries. Every transaction has a debit entry and a credit entry, and they must always balance to zero. If I transfer a hundred dollars from account A to account B, the ledger records a hundred-dollar debit from A and a hundred-dollar credit to B. The total is zero. Money is never created or destroyed on the ledger.

This double-entry property is the fundamental invariant. If at any point the sum of all debits doesn't equal the sum of all credits, something is wrong. This is how you detect errors, fraud, and bugs.

Now, the most important rule of a ledger system: it is append-only. You never update or delete entries. Ever. If you made a mistake, you create a correcting entry. This gives you a complete audit trail. You can reconstruct the balance of any account at any point in time by summing all entries up to that point.

In an interview, I'd start by designing the data model. The key tables are accounts, transactions, and entries. Each transaction has an ID, a timestamp, a type like payment, refund, or transfer, and a description. Each entry belongs to a transaction, has an account ID, an amount, and a direction: debit or credit. The constraint is that for every transaction, the sum of debits must equal the sum of credits.

This constraint must be enforced by the database, not the application. I'd use a database transaction that inserts all entries for a single financial transaction atomically. If the entries don't balance, the database rejects the transaction. This is where ACID is non-negotiable. You cannot have eventual consistency for a ledger. If two entries are written to different shards and one fails, you have an inconsistent ledger. That's a financial error.

So for the database, I'd use PostgreSQL with a single-leader replication model. The leader handles all writes, and followers serve reads. For the ledger specifically, I'd keep all entries for a single financial transaction on the same shard, using the transaction ID as the shard key. This way, the database can enforce the balance constraint within a single database transaction.

Now, what about performance? Let me estimate. Say we have a million accounts and 10,000 transactions per second. Each transaction creates 2 entries on average, so 20,000 entry writes per second. That's a lot for a single PostgreSQL instance.

The standard approach is to separate the write path from the read path using CQRS. The ledger is the write model: optimized for append-only writes with ACID guarantees. Account balances are the read model: pre-computed and cached for fast reads.

When a new transaction is committed to the ledger, a change data capture stream, or CDC, publishes the new entries to a message queue. A balance projection service consumes these events and updates the account balance in a read-optimized store, like Redis for hot accounts or a materialized view in PostgreSQL for all accounts.

This gives you the best of both worlds. The ledger has strong consistency and ACID guarantees. The balance queries are fast because they're reading pre-computed values.

But there's a subtlety. The balance in the read store is eventually consistent with the ledger. It might be a few milliseconds behind. For most operations, this is fine. But for some operations, like checking if an account has sufficient funds before a transfer, you need the real-time balance. For those, you'd query the ledger directly or use the database's transaction isolation to read the committed balance.

Let me also talk about audit and compliance. Financial regulations require that you can produce a complete audit trail for any account, showing every transaction in order, with timestamps, amounts, and the identity of who authorized each transaction. The append-only ledger gives you this automatically. You just query all entries for an account, ordered by timestamp.

But regulations also require that the data is tamper-proof. Someone with database access shouldn't be able to modify a ledger entry undetected. One approach is to store a hash chain, similar to a blockchain. Each entry includes the hash of the previous entry. If any entry is modified, the chain breaks and the tampering is detected. This is a lightweight way to add integrity verification without the overhead of a full blockchain.

For storage, with 10,000 transactions per second and 500 bytes per entry, that's about 5 megabytes per second, or about 430 gigabytes per day. With 7-year retention, that's about 150 terabytes. This is manageable with a sharded PostgreSQL setup.

The key trade-off in a ledger system interview is between consistency and performance. The ledger must have strong consistency, which limits write throughput on a single shard. CQRS and read models give you fast reads, but you need to handle the edge case where the read model is slightly behind the write model. And for financial operations that need real-time consistency, you need to query the ledger directly.

So... the key takeaways. Double-entry: every transaction must balance. Append-only: never update or delete. ACID: database-enforced consistency. CQRS: separate write and read models. Hash chain: tamper detection for compliance.

Great work today. See you next time."""
    },
    {
        "id": 33, "theme": "sd-fintech-trading",
        "title": "Trading Platform Think-Aloud",
        "subtitle": "Fintech: order matching, real-time feeds, FIFO",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're designing a trading platform, like a stock exchange. This is one of the hardest system design problems because of the extreme latency requirements. We're talking sub-millisecond matching, which means the architecture is fundamentally different from typical web systems.

Let me work through this step by step.

So, a trading platform matches buy and sell orders. The core component is the order book. For each instrument, like a stock, there's a list of buy orders sorted by price descending, called the bid side, and a list of sell orders sorted by price ascending, called the ask or offer side. The highest buy price is the best bid, and the lowest sell price is the best ask. The gap between them is the spread.

When a new order arrives, the matching engine checks if it can be filled. If someone submits a market buy order, it matches against the best ask. If someone submits a limit buy order at a price that meets or exceeds the best ask, it matches. If there's no match, the order sits in the book until a matching order arrives.

Within the same price level, orders are filled in FIFO order. First in, first out. This is price-time priority and it's a regulatory requirement in most markets. If two people submit limit buy orders at the same price, the one who submitted first gets filled first.

Now, the latency requirement. In modern trading, matching needs to happen in under a millisecond. Actually, in electronic trading, we're often talking microseconds. This means the matching engine must be in-memory, co-located with the exchange's network, and implemented in a high-performance language like C++ or Rust.

For this interview, I'll design a system that can match orders in under 10 milliseconds, which is reasonable for a web-based trading platform. For a real high-frequency trading exchange, you'd need a completely different architecture with FPGA-based matching engines and kernel-bypass networking. But that's out of scope.

Let me estimate the scale. 100,000 orders per second. 10 million trades per day. 5,000 instruments. Each order is about 200 bytes, and each trade is about 300 bytes.

The architecture has several components. First, the order gateway, which receives orders from clients via FIX protocol or a REST API. The gateway validates the order, checks risk limits, and forwards it to the matching engine.

The matching engine is the core. It maintains the order book for each instrument in memory. When a new order arrives, it tries to match it against existing orders. If there's a match, it creates a trade and updates the order book. If there's no match, it inserts the order into the book. The matching engine must be single-threaded per instrument to maintain ordering guarantees. But different instruments can be processed on different threads or different machines.

After a trade is executed, the matching engine publishes the trade to the market data service. The market data service broadcasts the trade to all subscribers via WebSocket or a dedicated multicast feed. This is the real-time market data that traders see on their screens: last price, volume, bid-ask spread, and order book depth.

The risk management service runs in parallel. Before an order is sent to the matching engine, the risk service checks that the trader has sufficient margin, isn't exceeding position limits, and isn't violating any circuit breakers. Circuit breakers are market-wide halts that trigger when prices move too far too fast. They're a regulatory requirement to prevent flash crashes.

For persistence, I'd use a write-ahead log, or WAL, for the matching engine. Every order and every trade is written to the WAL before being processed. This ensures that if the matching engine crashes, it can recover by replaying the WAL. The WAL is written sequentially, which is very fast even on SSDs.

For the order book data structure, I'd use a combination of a hash map and a sorted data structure. The hash map maps order IDs to orders for O(1) lookup. The sorted structure, like a skip list or a balanced tree, maintains the price levels for the bid and ask sides. This gives O(log N) insertion and O(1) access to the best bid and best ask.

For the market data feed, the key challenge is fan-out. Millions of subscribers want real-time data for thousands of instruments. I'd use a pub-sub architecture. The matching engine publishes trades and book updates to a message broker. The market data service subscribes and broadcasts to clients. For the highest performance, I'd use UDP multicast instead of TCP, which avoids the overhead of per-connection state.

The clearing and settlement process happens after the trade. In real markets, settlement is T plus 2, meaning two business days after the trade. The clearing house acts as the counterparty to both sides, guaranteeing that the trade will settle even if one party defaults. For our design, I'd mention that settlement is asynchronous and uses a separate clearing system.

So... what are the bottlenecks? Matching engine latency: must be sub-10ms, which means in-memory processing and single-threaded matching per instrument. Market data fan-out: millions of subscribers, which requires efficient broadcasting. Order book updates: at peak, hundreds of thousands of book changes per second, which must be reflected in the market data feed without delay.

The key trade-off in a trading platform interview is between latency and throughput. Single-threaded matching gives the lowest latency but limits throughput per instrument. You can increase throughput by partitioning across instruments, but you can't parallelize matching within a single instrument without sacrificing ordering guarantees.

Another important trade-off is reliability versus performance. The write-ahead log adds latency because every operation must be persisted before being committed. You can reduce this by batching WAL writes, but this increases the risk of data loss in a crash.

Great work today. See you next time."""
    },
    {
        "id": 34, "theme": "sd-fintech-fraud",
        "title": "Fraud Detection Think-Aloud",
        "subtitle": "Fintech: stream processing, feature stores, rules vs ML",
        "playlist_id": "sd-think-aloud",
        "script": """Welcome to System Design Think-Aloud. Today we're designing a fraud detection system. This is a fascinating problem because it's at the intersection of real-time stream processing, machine learning, and human operations. And it has one of the most interesting trade-offs in all of system design: catching more fraud versus creating more false positives that annoy legitimate customers.

Let me work through this step by step.

So, the problem is: detect fraudulent transactions in real-time. When a transaction comes in, we need to decide within 100 milliseconds whether to approve it, flag it for review, or reject it. And we need to be right most of the time. But here's the hard part. If we're too aggressive, we block legitimate transactions, which angers customers and loses revenue. If we're too lenient, fraudsters steal money.

Let me estimate the scale. Say we're processing 10,000 transactions per second. The fraud rate is about 0.1 percent, which means roughly 10 fraudulent transactions per second. Our false positive rate target is under 5 percent, meaning fewer than 500 out of every 10,000 legitimate transactions should be incorrectly flagged.

The architecture has three layers. The rules engine, the ML scoring engine, and the manual review queue. Let me think through each.

The rules engine is the first line of defense. It runs deterministic rules that catch obvious fraud. Things like: transaction amount exceeds a threshold, more than 5 transactions from the same card in 10 minutes, transaction from a country the user has never visited, or a device fingerprint that's on a known fraud list. Rules are fast because they're just lookups and comparisons. They can execute in under 10 milliseconds.

The rules engine needs access to real-time features. A feature is a data point about the transaction or the user's recent activity. Examples include: the number of transactions in the last hour, the average transaction amount over the last 30 days, the geographic distance between the current transaction and the last one, and the device fingerprint's fraud history.

These features need to be computed in real-time and stored in a feature store. The feature store is a critical component. It maintains a rolling window of features for each user and each card. When a new transaction arrives, the features are updated and stored for the next transaction.

I'd implement the feature store using Redis with sorted sets for time-windowed features. For example, to count transactions in the last hour, I'd add each transaction's timestamp to a sorted set. When I need the count, I remove entries older than one hour and return the size of the set. Redis makes this fast with ZREMRANGEBYSCORE and ZCARD commands.

The ML scoring engine is the second layer. For transactions that pass the rules engine, we run them through a machine learning model that scores the probability of fraud. The model is trained on historical transaction data with labeled outcomes: confirmed fraud or confirmed legitimate.

The model takes the real-time features as input and outputs a score between 0 and 1. If the score exceeds a threshold, say 0.8, the transaction is rejected automatically. If it's between 0.5 and 0.8, it's flagged for manual review. Below 0.5, it's approved.

For the ML model, I'd use a gradient-boosted decision tree like XGBoost. It's interpretable, which is important for regulatory compliance because you need to explain why a transaction was rejected. It's also fast to score, typically under 10 milliseconds per transaction.

The model needs to be retrained regularly because fraud patterns evolve. This is concept drift. A model trained on January's data might not catch March's fraud techniques. I'd set up a daily retraining pipeline that uses the previous 90 days of labeled data. The new model is deployed as a canary, running alongside the old model, and we compare their performance before fully switching.

Now, the manual review queue. Transactions that are flagged for review go to a queue that human analysts review. The analysts can see the transaction details, the user's history, the triggered rules, and the ML score. They make the final decision: approve or reject. Their decisions are fed back into the training data, which improves the model over time.

This feedback loop is critical. Without it, the model can't improve. Every confirmed fraud case and every false positive is a training example. The more examples we have, the better the model gets.

For the streaming architecture, I'd use Apache Kafka or a similar stream processing system. When a transaction arrives, it's published to a Kafka topic. The rules engine consumes from this topic, computes features, applies rules, and publishes the result to another topic. The ML engine consumes from that topic, scores the transaction, and publishes the final decision.

This pipeline needs to complete within 100 milliseconds. Let me think about the timing. Kafka consumption: 5 milliseconds. Feature computation: 10 milliseconds. Rule evaluation: 5 milliseconds. ML inference: 10 milliseconds. Kafka publishing between steps: 10 milliseconds total. That's about 40 milliseconds, which gives us comfortable headroom within our 100-millisecond budget.

For the data store, I'd use Cassandra for the transaction history. It's optimized for high write throughput and time-series queries. The feature store in Redis handles the real-time features. And a data warehouse like BigQuery stores the full transaction history for model training and reporting.

So... what are the bottlenecks? Feature computation latency: every transaction needs up-to-date features, which means the feature store must handle 10,000 reads and writes per second with low latency. Model drift: fraud patterns change, so the model must be retrained regularly without downtime. And false positive impact: every false positive is a customer who might leave. The business cost of false positives can exceed the cost of actual fraud.

The key trade-off in a fraud detection interview is the precision-recall trade-off. Higher precision means fewer false positives but might miss more fraud. Higher recall means catching more fraud but annoying more legitimate customers. In an interview, you should explicitly name this trade-off and explain how you'd set the threshold based on the business's risk tolerance.

Another important point: the system should be designed for incremental improvement. Start with rules, add ML on top, and continuously retrain. Don't try to build a perfect ML model from day one. Rules catch the obvious stuff and give you labeled data to train the ML model. The ML model catches the subtle patterns that rules miss. And the human reviewers handle the edge cases that both miss.

Great work today. See you next time."""
    },
]


def main():
    print("=== generate_sd.py (think-aloud format) ===")

    data_dir = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
    os.makedirs(data_dir, exist_ok=True)

    theme = sys.argv[1] if len(sys.argv) > 1 else None

    if theme:
        configs = [ec for ec in THINK_ALOUD_EPISODES if ec["theme"] == theme]
        if not configs:
            print(f"ERROR: Unknown theme '{theme}'. Available: {[e['theme'] for e in THINK_ALOUD_EPISODES]}")
            sys.exit(1)
    else:
        configs = THINK_ALOUD_EPISODES

    results = []

    for config in configs:
        print(f"\n--- #{config['id']}: {config['title']} ---")

        script = config["script"]
        word_count = len(script.split())
        est_min = word_count / 140
        print(f"  Script: {word_count} words, ~{est_min:.0f} min estimated")

        script_path = os.path.join(data_dir, f"sd-{config['theme']}.txt")
        with open(script_path, "w") as f:
            f.write(script)

        mp3_path = os.path.join(data_dir, f"sd-{config['theme']}.mp3")
        print(f"  Generating audio (BrianNeural)...")
        synthesize(script, mp3_path, voice="narrator")

        size_mb = os.path.getsize(mp3_path) / (1024 * 1024)
        duration = get_duration_str(mp3_path)
        print(f"  MP3: {size_mb:.1f} MB, {duration}")

        results.append({
            "id": config["id"],
            "theme": config["theme"],
            "title": config["title"],
            "subtitle": config["subtitle"],
            "playlist_id": config["playlist_id"],
            "script_path": script_path,
            "mp3_path": mp3_path,
            "file_size_bytes": os.path.getsize(mp3_path),
            "duration": duration
        })

    results_path = os.path.join(data_dir, "sd_episodes.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone — {len(results)} SD think-aloud episodes generated")


if __name__ == "__main__":
    main()
