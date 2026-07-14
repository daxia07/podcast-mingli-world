"""Mock Interview: Bulk Payouts & Payroll-Style Batch Payments — Two-voice dialogue."""


def build():
    lines = []

    # SECTION 1: Requirements
    lines.append(("interviewer", "Hi, welcome. Today I'd like you to design a bulk payout system. A business uploads a file with up to one million supplier payouts in multiple currencies. It needs validation feedback, all-or-nothing behavior where possible, approvals, scheduled execution, progress tracking, per-payment status, retries, and a downloadable result file. The platform must avoid duplicating payments if the upload or worker is retried, and must not overload a bank partner during a large batch."))

    lines.append(("candidate", "Thanks. Bulk payouts combine the complexity of individual payments — idempotency, compliance, bank integration — with the additional challenges of batch processing: streaming validation, aggregate funding, partner rate limiting, and partial failure semantics. The key insight is that a batch is a durable aggregate with independently idempotent payment items. Let me clarify the requirements. First, what's the maximum file size and row count? And what formats do we support?"))

    lines.append(("interviewer", "Up to one million rows. CSV and XLSX formats. Each row has: beneficiary name, account number, sort code or routing number, amount, currency, and a client reference. Some rows will be invalid — wrong account format, unsupported currency, amount exceeds limits. The user needs to see which rows are valid and which have errors before approving."))

    lines.append(("candidate", "Second question: is partial execution allowed? If one item in a batch of a thousand fails, do the other nine hundred ninety-nine still execute?"))

    lines.append(("interviewer", "Yes for execution — each item proceeds independently. But for funding, the business wants to know the total cost upfront. If they don't have enough funds for the whole batch, we should fail validation, not execute a subset. Unless they opt into partial funding as a product feature."))

    lines.append(("candidate", "Third question: what about approval workflows? Does every batch need a human approval, or can small batches auto-approve?"))

    lines.append(("interviewer", "Batches over a configurable threshold — say ten thousand dollars total — require dual approval. Below that, the uploader can approve their own batch. Scheduled execution is supported — the user can set a future execution date."))

    lines.append(("candidate", "Summary: million-row files, CSV and XLSX, row-level validation with feedback, aggregate funding check before execution, independent per-item execution, dual approval for large batches, scheduled execution, partner rate limiting, idempotent retries, and per-item status tracking. Moving to architecture."))

    # SECTION 2: Architecture
    lines.append(("interviewer", "Show me the architecture."))

    lines.append(("candidate", "The batch lifecycle has seven stages. Stage one: upload. The user uploads the file through the API. The upload service runs malware and format checks, stores the file in encrypted object storage — S3 or R2 — with a hash for integrity, and creates a batch record in the database with status uploaded. A repeat upload with the same idempotency key returns the existing batch — no duplicate batches."))

    lines.append(("candidate", "Stage two: validation. A streaming parser reads the file row by row, without loading the entire file into memory. For each row, it canonicalizes fields — trim whitespace, normalize currency codes, validate account number formats per country. It checks business rules: supported currency, amount within limits, beneficiary not on sanctions list. Valid rows receive a deterministic item key — tenant plus batch ID plus client reference. Duplicate client references within the same batch are a validation error. Invalid rows get an error code and message. The validation results are stored per item, and the user sees a summary: nine hundred thousand valid, ten thousand invalid, with details on each error."))

    lines.append(("candidate", "Stage three: correction and approval. The user can fix errors and re-upload, creating a new batch version, or delete invalid items and proceed with the valid ones. When ready, they submit for approval. Approval freezes the batch — no more changes. A second approver — for batches above the threshold — reviews and approves. The system calculates the total amount per currency and reserves the aggregate funding through the ledger posting service."))

    lines.append(("candidate", "Stage four: scheduling. The scheduler queues the batch for execution at the specified date and time. It considers partner cut-off times — if a batch for Australian banks is submitted after the ACH cut-off, it should be scheduled for the next business day. The scheduler respects partner capacity: each partner has a maximum concurrent payments limit, and the scheduler only emits work items when there's capacity."))

    lines.append(("candidate", "Stage five: execution. Workers claim items from the work queue using leases — a worker gets an item, processes it within a lease period, and either completes it or the lease expires and another worker picks it up. Each item goes through the normal payment workflow — compliance checks, FX conversion if needed, bank adapter submission. The item uses the same idempotency rules as a single payment — the item key is the idempotency key for the payment service. If a worker crashes, the lease expires, and another worker retries the same item using its durable idempotency key — no duplicate payments."))

    lines.append(("candidate", "Stage six: status tracking. The batch status is a projection of item outcomes: completed, completed with errors, or partially cancelled. The user can see per-item status in real-time — submitted, processing, settled, failed, unknown. Stage seven: results export. A downloadable results file is generated from the immutable item and result records, including the original row, the payment ID, the final status, and any failure reasons."))

    # SECTION 3: Deep Dive — State Machine and Idempotency
    lines.append(("interviewer", "Walk me through the batch state machine and how you prevent duplicate payments when a worker is retried."))

    lines.append(("candidate", "The batch state machine: uploaded, validating, needs correction, ready for approval, approved, scheduled, executing, completed, or completed with errors. From approved, the user can also cancel before execution starts. From executing, the user can cancel items not yet submitted — but items already sent to the bank continue through the normal payment lifecycle and reconciliation. Partial cancellation is the realistic outcome — you can't unsend a payment that's already been submitted to a bank."))

    lines.append(("candidate", "Item idempotency is the key to preventing duplicate payments. Each item has a deterministic key: tenant, batch ID, client reference. When the worker calls the payment service, it passes this key as the idempotency key. The payment service looks up the key — if a payment already exists for this key, it returns the existing payment's status, not a new payment. This means: if a worker crashes after submitting the payment to the bank but before updating the item status, the next worker that picks up the item will call the payment service, which will find the existing payment and return its current status — maybe submitted, maybe settled. No duplicate submission."))

    lines.append(("candidate", "But here's the subtlety: what if the worker crashes before calling the payment service? Then no payment exists, and the next worker correctly starts a new one. What if the worker crashes after the payment service created the payment but before the bank adapter sent it? Then the payment exists in created state, and the next worker's call to the payment service returns the existing payment, and the payment workflow resumes from where it left off — it submits to the bank adapter. The payment's own state machine and idempotency handle this resumption correctly. The batch worker doesn't need to know about the payment's internal state — it just calls the payment service and records the result."))

    # SECTION 4: Deep Dive — Partner Rate Limiting
    lines.append(("interviewer", "How do you avoid overloading a bank partner during a large batch?"))

    lines.append(("candidate", "This is where the scheduler and work queue design are critical. Each partner — each bank or payment rail — has a known capacity. For example, the Australian ACH accepts up to five hundred transactions per second. A smaller partner bank in Vietnam might handle only fifty per second. The scheduler maintains per-partner queues with token bucket or concurrency-based rate limits. When a batch has ten thousand items going through the same Australian bank, the scheduler emits work at a rate the bank can handle — maybe four hundred per second to leave headroom for single payments from other sources."))

    lines.append(("candidate", "The work queue uses a partner-sharded design. Items are partitioned by their target partner, and each partner partition has its own queue with its own rate limit. Workers consume from partner queues, not from a single global queue. This prevents a large batch from monopolizing worker capacity — if one partner is slow, it doesn't block items for faster partners."))

    lines.append(("candidate", "Adaptive backoff: if a partner starts returning rate-limit errors — HTTP four twenty nine or a custom bank response code — the scheduler reduces the emission rate for that partner. It also respects bank cut-off times: if the Australian bank's cut-off is four PM AEST, the scheduler prioritizes Australian items earlier in the day and shifts remaining items to the next business day. Missing a cut-off means the payment settles a day later, which impacts the business's payment commitments."))

    # SECTION 5: Failure Scenarios
    lines.append(("interviewer", "The user cancels a batch that's partially executed. What happens?"))

    lines.append(("candidate", "Cancellation applies to items not yet submitted to the bank. The system marks those items as cancelled and releases their reserved funding back to available. Items already submitted — in submitted, processing, or unknown state — cannot be cancelled. They continue through the normal payment lifecycle. The user sees a partial cancellation: eight hundred items cancelled, two hundred items already submitted and continuing. The final batch status is partially cancelled, and the results file lists each item's outcome — cancelled, or the final payment status."))

    lines.append(("candidate", "This is the realistic answer. Truly atomic all-or-nothing execution is impossible in a distributed financial system — once a payment instruction reaches a bank, you can't claw it back unilaterally. All-or-nothing applies to validation and funding acceptance, not to settlement across banks. The user needs to understand this limitation, and the UI makes it clear: cancellation affects only unsubmitted items."))

    lines.append(("interviewer", "A worker crashes after claiming an item. How do you ensure the item is eventually processed?"))

    lines.append(("candidate", "The lease mechanism handles this. When a worker claims an item, it gets a lease with a timeout — say five minutes. The worker must either complete the item or renew the lease within that period. If the worker crashes, the lease expires, and the item returns to the available state in the work queue. Another worker claims it and starts processing. Because of item idempotency, the new worker's call to the payment service is safe — it either starts a new payment or resumes an existing one, but never creates a duplicate."))

    lines.append(("interviewer", "The aggregate funding reservation fails because the account doesn't have enough funds for the entire batch. What do you do?"))

    lines.append(("candidate", "Fail the approval step. The user is told the total amount required and the current available balance. They can either top up their account, reduce the batch size by removing items, or — if the product supports partial funding — opt into executing only the items that fit within the available balance. But the default is fail-fast: if you can't fund the whole batch, don't start any of it. Starting an arbitrary subset without explicit user consent is a product risk — the user expects all items to execute, and partial execution without consent is a trust violation."))

    # SECTION 6: Scale
    lines.append(("interviewer", "How do you handle a one-million-row file?"))

    lines.append(("candidate", "The file is stored in object storage, not in the database. A streaming parser reads it row by row — maybe in chunks of ten thousand rows — and bulk-inserts items into the database in bounded chunks. We don't use a single database transaction for a million rows — that would lock the table for too long and risk an out-of-memory rollback. Instead, each chunk is its own transaction, and the batch record tracks the overall validation progress — rows processed, rows valid, rows invalid — as an atomic counter updated after each chunk."))

    lines.append(("candidate", "Progress reporting: the user polls or subscribes to a WebSocket that streams validation progress. After all chunks are processed, the user sees the full summary and can drill into errors. The key principle: never load the entire file into memory, never use a single transaction for a million rows, and always stream."))

    # SECTION 7: Summary with Killer Phrases
    lines.append(("candidate", "Let me close with the killer phrases for bulk payouts. One: a batch is a durable aggregate with independently idempotent items — the batch tracks overall state, but each item has its own lifecycle and idempotency key. Two: stream, don't load — parse files row by row, bulk-insert in chunks, never hold a million rows in memory or in a single transaction. Three: all-or-nothing for validation and funding, not for settlement — once a payment reaches a bank, it can't be unsent. Four: partner-sharded work queues with per-partner rate limits — a large batch must not monopolize a bank's capacity. Five: lease-based worker claims with item idempotency — if a worker crashes, the lease expires, the next worker resumes safely via the payment service's idempotency. Six: cancellation affects only unsubmitted items — partial cancellation is the realistic outcome. Seven: aggregate funding reservation before execution — fail the approval if funds are insufficient, don't execute an arbitrary subset. Eight: deterministic item key is tenant plus batch ID plus client reference — this is the idempotency key for the payment service. The phrase to remember: a batch is a durable aggregate with independently idempotent items."))

    lines.append(("interviewer", "Walk me through a complete batch payout flow."))

    lines.append(("candidate", "Step one: upload. A Singapore e-commerce company uploads a CSV file with fifty thousand supplier payouts — a mix of AUD, USD, and SGD payments. The upload service stores the file in R2 with a SHA-256 hash, creates a batch record, and returns a batch ID to the user."))

    lines.append(("candidate", "Step two: validation. The streaming parser reads the file in ten-thousand-row chunks. For each row, it validates: beneficiary account format matches the country, currency is supported, amount is positive and within limits, client reference is unique within the batch. Forty-nine thousand eight hundred rows pass. Two hundred rows fail — fifty have invalid Australian BSB format, one hundred have amounts exceeding the per-transaction limit, and fifty have duplicate client references. The user sees the validation summary and the error details."))

    lines.append(("candidate", "Step three: correction. The user fixes the invalid BSB codes and removes the duplicate references and over-limit items. They re-upload the corrected rows, creating a new batch version. The updated count is forty-nine thousand nine hundred fifty valid items."))

    lines.append(("candidate", "Step four: approval. The total amount is two point five million SGD equivalent — above the dual-approval threshold. The uploader submits for approval. A second approver in the finance team reviews the batch summary and approves. The system reserves two point five million SGD from the company's available balance through the ledger posting service."))

    lines.append(("candidate", "Step five: scheduling. The batch is scheduled for execution at nine AM Singapore time the next business day. The scheduler calculates partner cut-off times: AUD items must be submitted before four PM AEST, USD items before five PM EST, SGD items before three PM SGT. It prioritizes accordingly."))

    lines.append(("candidate", "Step six: execution. At nine AM, the scheduler starts emitting work items to partner-sharded queues. The Australian bank queue emits at four hundred items per second. Workers claim items, call the payment service with idempotency keys, and track results. By noon, thirty thousand items have settled. By four PM, forty-nine thousand items settled, nine hundred fifty are in processing, and one has failed — beneficiary account closed. The failed item's reserved funds are released back to available."))

    lines.append(("candidate", "Step seven: results. The user downloads the results file: each original row with its payment ID, status, and any failure reason. The batch status is completed with one error. The aggregate funding is finalized — forty-nine thousand nine hundred forty-nine items settled, one failed, funds for the failed item released. The company's available balance reflects the final outcome. A batch is a durable aggregate with independently idempotent items."))

    return lines
