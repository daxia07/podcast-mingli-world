"""Mock Interview: Multi-Currency Wallet & Double-Entry Ledger — Two-voice dialogue."""


def build():
    lines = []

    # SECTION 1: Requirements
    lines.append(("interviewer", "Hi, welcome. Today I'd like you to design the wallet and ledger behind a global payments platform. A business can hold SGD, AUD, USD, and EUR balances, receive money, convert funds, make payouts, and see a transaction history. The system must prevent overspending, support pending holds and reversals, survive retries and concurrent writes, and produce an audit trail suitable for financial operations. Assume ten million accounts, one hundred million journal lines per day, and a requirement to reconstruct any balance at any point in time. Start by clarifying the requirements."))

    lines.append(("candidate", "Thanks. The wallet and ledger is the financial backbone of the platform — every payment, FX conversion, fee, and settlement flows through it. The key insight is that we need to separate the immutable journal, which is the source of truth, from balance projections, which are derived and optimized for reads. Let me clarify the boundaries. First, is this a stored-value wallet where we hold customer funds, an internal ledger for safeguarded client funds, or both?"))

    lines.append(("interviewer", "Both. The platform holds customer funds in safeguarded accounts, and customers can also top up their wallets for faster payouts. The wallet is the customer-facing view; the ledger is the internal source of truth."))

    lines.append(("candidate", "Second question: which currencies and decimal rules apply? Are negative balances, credit lines, and pending card authorizations in scope?"))

    lines.append(("interviewer", "Four currencies: SGD, AUD, USD, EUR. All use two decimal places. Negative balances are not allowed for wallets — a payment that would overdraw must be declined. Pending card authorizations are in scope — they hold funds but don't settle immediately. Credit lines are out of scope for now."))

    lines.append(("candidate", "Third question: is balance read-your-writes required after a transfer? What's the target p99 for a debit?"))

    lines.append(("interviewer", "Yes, read-your-writes after a transfer — the merchant should see the updated balance immediately. P99 for a debit should be under fifty milliseconds for the balance check and under two hundred milliseconds for the full posting."))

    lines.append(("candidate", "Let me summarize: immutable double-entry journal as source of truth, balance projections for reads, four two-decimal currencies, no negative wallet balances, pending holds for card authorizations, read-your-writes, p99 debit under two hundred milliseconds, ten million accounts, one hundred million journal lines per day. Moving to estimation."))

    # SECTION 2: Estimation
    lines.append(("interviewer", "Go ahead with the numbers."))

    lines.append(("candidate", "One hundred million journal lines per day. Each journal has at least two lines — debit and credit — so about fifty million journal transactions per day. Average throughput is about five hundred seventy journals per second. Peak during business hours — say three to five times average — that's about seventeen hundred to twenty-eight hundred journals per second. That's significant but manageable with a well-partitioned relational database."))

    lines.append(("candidate", "Storage: each journal line is about two hundred bytes — account ID, currency, amount, direction, journal ID, timestamp, posting type, business reference. One hundred million lines times two hundred bytes is about twenty gigabytes per day. Over three years with retention, that's about twenty terabytes of journal data. We'd partition by posting month and archive older partitions to colder storage, but keep the indexes hot for operational queries."))

    lines.append(("candidate", "Balance reads: ten million accounts, but the read pattern is much heavier than writes. A merchant checking their balance, a payment service verifying available funds, a dashboard refreshing — probably ten to fifty reads per account per day. That's one hundred million to five hundred million balance reads per day. This is why we maintain materialized balance projections rather than recomputing from journals on every read."))

    # SECTION 3: High-Level Architecture
    lines.append(("interviewer", "Let's see the architecture."))

    lines.append(("candidate", "The core principle: the ledger posting service is the only writer of journal entries. Product services — payments, FX, fees, card authorization — ask it to reserve, release, transfer, convert, or post a fee. They never update a balance column directly. Here's the flow. The command API receives a posting request — say, reserve one hundred AUD for a payout. The request includes an idempotency key, posting type, business reference, and the journal lines. The posting service validates the request, checks the balance invariant — available must be greater than or equal to the debit amount — and then in a single database transaction writes the journal lines, updates the balance projection, and writes an outbox event. The outbox event drives downstream projections, notifications, and reporting asynchronously."))

    lines.append(("candidate", "The journal table is append-only. Each journal entry has a journal ID, currency, account, direction — debit or credit — monetary amount, effective time, posting type — like reserve, settle, release, fee, FX conversion — and business reference — like the payment ID. The critical invariant: all lines in each journal, grouped by currency, must balance. Debits equal credits for every currency. A cross-currency FX conversion has balanced source-currency and target-currency legs plus FX clearing and revenue accounts — it is never one journal with a fake zero sum across currencies."))

    lines.append(("candidate", "The balance projection table has account ID, currency, available amount, reserved amount, and a version number. The version is crucial for concurrency control. When we debit available funds, we use a conditional update — update where version equals expected version and available greater than or equal to debit amount. If the version changed or funds are insufficient, the transaction fails and we retry. This is optimistic concurrency control for the common case, with a fallback to select for update for hot accounts."))

    # SECTION 4: Deep Dive — Posting and Concurrency
    lines.append(("interviewer", "Walk me through a concrete example — a payout flow from reservation to settlement."))

    lines.append(("candidate", "Let's say a merchant in Singapore wants to pay a supplier one thousand AUD. Step one: the payment service calls the ledger posting service with a reserve request. The posting service, in one transaction, does the following. First, select the merchant's account balances for AUD with a row lock — select for update. Second, check that available is at least one thousand AUD. Third, write two journal lines: debit customer available AUD one thousand, credit customer reserved AUD one thousand. Fourth, update the balance projection: available minus one thousand, reserved plus one thousand, version incremented. Fifth, write an outbox event for the payment service to proceed. The transaction commits, and the merchant's balance immediately shows one thousand less available. Read-your-writes satisfied."))

    lines.append(("candidate", "Step two: the payment workflow processes the payout through the banking system. This takes one to two business days. The money is sitting in reserved — it's committed to this payout but not yet gone from the platform."))

    lines.append(("candidate", "Step three: when the bank confirms settlement, the payment service calls the ledger posting service with a settle request. In one transaction: debit customer reserved AUD one thousand, credit partner payable AUD one thousand. Update balances: reserved minus one thousand. Write outbox event for notification. The merchant's reserved balance decreases, and the partner's payable increases. The merchant's available balance is unchanged — it was already debited in step one."))

    lines.append(("candidate", "What if the payout fails? The payment service calls release. In one transaction: debit customer reserved AUD one thousand, credit customer available AUD one thousand. The funds return to available. The journal records the full lifecycle — reserve, then release — and an auditor can trace exactly what happened and why."))

    lines.append(("interviewer", "What about concurrent debits on the same account? Two payments trying to reserve funds at the same time."))

    lines.append(("candidate", "This is the critical concurrency problem. If two payments each try to reserve one thousand AUD from an available balance of fifteen hundred, one must fail. With optimistic concurrency control, each transaction reads the current version and attempts to update where available greater than or equal to one thousand and version equals the read version. One transaction will find the version has changed and fail. The failed transaction retries — but now it sees the updated available balance of five hundred, which is insufficient, so it declines. No overspend."))

    lines.append(("candidate", "For extremely hot accounts — an account with hundreds of concurrent debits — optimistic retry becomes a performance problem. The fallback is to partition the account into sub-accounts, each with its own version and balance, and stripe incoming requests across sub-accounts. Or use a single-writer pattern where all debits for a given account go through a partitioned queue processed by a single worker. This sacrifices some concurrency but guarantees no overspend without retries. The key principle: serialize per account, not globally. Every account should not share a global lock."))

    # SECTION 5: Deep Dive — FX Conversion and Rounding
    lines.append(("interviewer", "How does an FX conversion work in the ledger? You're converting SGD to AUD — show me the journal entries."))

    lines.append(("candidate", "An FX conversion is a multi-leg journal with balanced entries in each currency. Say the merchant converts one thousand SGD to Australian dollars at a rate of one point one two. Step one: debit customer available SGD one thousand. Step two: credit customer available AUD one thousand one hundred twenty. But wait — these don't balance individually. The SGD side has a one thousand debit with no credit, and the AUD side has a one thousand one hundred twenty credit with no debit. We need clearing accounts. Step three: credit FX clearing SGD one thousand — this balances the SGD leg. Step four: debit FX clearing AUD one thousand one hundred twenty — this balances the AUD leg. But now FX clearing has one thousand SGD credit and one thousand one hundred twenty AUD debit, which is an imbalance. Step five: the FX revenue account captures any spread. If the mid-market rate is one point one two one and we charged one point one two, the spread is one AUD on one thousand SGD — that's approximately ten AUD. We debit FX clearing AUD ten, credit FX revenue AUD ten. Now every currency balances individually."))

    lines.append(("candidate", "Rounding is critical. Each currency has its permitted decimal scale — two for SGD, AUD, USD, EUR, but zero for JPY. We store amounts at the currency's scale using a documented rounding mode — typically half-even, also known as banker's rounding. When rounding creates a penny discrepancy, we post an explicit rounding entry so every journal still balances. The rounding account itself is periodically reviewed — large rounding accumulations indicate a problem with the rate or calculation logic."))

    # SECTION 6: Failure Modes and Recovery
    lines.append(("interviewer", "What happens when there's a database failover?"))

    lines.append(("candidate", "Database failover in a ledger system must prevent split brain. If two database nodes both think they're primary, they could both accept writes, creating divergent journals and corrupted balances. Our failover sequence: detect primary failure through independent health signals. Fence the old primary — revoke its write credentials and reject any connections from it. Verify that a synchronous replica in another availability zone has all committed data — this is our durability guarantee. Promote the replica to primary. Update routing. Only then do we accept writes again. Split brain is worse than temporary unavailability. I'd rather have a two-minute outage than a two-hour reconciliation nightmare."))

    lines.append(("interviewer", "What about an imbalance alert — the system detects that debits don't equal credits for some currency?"))

    lines.append(("candidate", "This is the nightmare scenario for a financial system, and the response must be immediate. First, if the imbalance is systemic — affecting many journals — we block the affected posting path. No new journals are written until we understand the root cause. Second, identify the specific journal IDs causing the imbalance. The invariant check runs on every posting, so a committed imbalance means either a bug in the posting logic or a database-level corruption. Third, restore balance projections from journal replay — recompute all balances from the immutable journal history and compare with the current projections. Fourth, repair only with approved compensating entries — never edit a historical journal. The repair is itself a journal, linked to the original by a correction reference, with an approval audit trail. And fifth, root-cause the bug and deploy a fix before re-enabling the posting path."))

    # SECTION 7: Idempotency and Rebuilding
    lines.append(("interviewer", "How do you handle idempotency for ledger postings?"))

    lines.append(("candidate", "Idempotency is keyed on tenant, posting type, and business reference. For example, a payment with ID pay one two three has a reserve posting and a settle posting. The reserve uses business reference pay one two three reserve. If the payment service retries the reserve — because it got a timeout — the ledger posting service looks up the existing journal by the idempotency key and returns the original journal ID and result. No duplicate journal entries. This is critical for financial integrity — double-posting a debit would steal money from the customer."))

    lines.append(("candidate", "How do we rebuild balances? Start from a verified snapshot — a point-in-time balance dump that was reconciled and signed off. Then replay all immutable journals in order from that point. Compare the computed balances with the current projections. If they match, the projections are correct. If they differ, investigate and repair with compensating entries. Then swap the rebuilt projections for the live ones. This rebuild process is how we prove no money was lost — per-journal and per-currency balance checks, control-account reconciliation, and daily trial balance all verify the invariant."))

    # SECTION 8: Summary with Killer Phrases and E2E Walkthrough
    lines.append(("candidate", "Let me close with the killer phrases for this topic. One: the journal is the source of truth, balances are projections — never update a balance directly, always post a journal. Two: every journal must balance per currency — debits equal credits, never a fake zero sum across currencies. Three: corrections are compensating journals, never edits to history — append-only, immutable audit trail. Four: serialize per account, not globally — optimistic concurrency with conditional version checks, fallback to partitioned single-writer for hot accounts. Five: split brain is worse than temporary unavailability — fence the old primary before promoting a new one. Six: idempotency key is tenant plus posting type plus business reference — a retry returns the original result, never a duplicate posting. Seven: FX conversion has balanced legs per currency plus clearing and revenue accounts — the spread goes to FX revenue, not into the void. And eight: rounding entries are explicit — every rounding discrepancy is a journal line, making the system auditable. The phrase to remember: the journal is the source of truth, balances are projections."))

    lines.append(("interviewer", "Walk me through the complete flow for a merchant converting SGD to AUD and then making a payout."))

    lines.append(("candidate", "Step one: FX conversion. The merchant requests to convert one thousand SGD to AUD at a quoted rate of one point one two. The ledger posting service receives the request with idempotency key merchant four two FX convert one two three. In one transaction: debit customer available SGD one thousand, credit FX clearing SGD one thousand — SGD leg balanced. Credit customer available AUD one thousand one hundred twenty, debit FX clearing AUD one thousand one hundred ten — the mid-market amount. Debit FX clearing AUD ten, credit FX revenue AUD ten — the spread. AUD leg balanced. Update balance projections: merchant available SGD minus one thousand, available AUD plus one thousand one hundred twenty. Version incremented. Outbox event fires. The merchant sees their updated balances immediately."))

    lines.append(("candidate", "Step two: payout reservation. The merchant requests a payout of five hundred AUD to a supplier. Payment service calls ledger: reserve five hundred AUD for pay four five six. In one transaction: debit customer available AUD five hundred, credit customer reserved AUD five hundred. Balance projection updated: available AUD minus five hundred, reserved AUD plus five hundred. The merchant sees available balance decreased, and a pending payout in their dashboard."))

    lines.append(("candidate", "Step three: payout settlement, two business days later. Bank confirms the five hundred AUD arrived at the supplier. Payment service calls ledger: settle pay four five six. In one transaction: debit customer reserved AUD five hundred, credit partner payable AUD five hundred. Reserved returns to zero, partner payable increases. The payout is complete. The merchant's transaction history shows: FX conversion of one thousand SGD, payout of five hundred AUD, and remaining available balance of six hundred twenty AUD — all derived from the immutable journal entries, all auditable, all balancing."))

    lines.append(("candidate", "And if the payout had failed, we'd release instead of settle: debit reserved, credit available. The funds return, and the journal records the full arc — reserve, then release. An auditor can reconstruct the complete financial story from the journal alone, without needing any external system. That's the power of an immutable double-entry ledger: it's not just accounting, it's proof. The journal is the source of truth, balances are projections."))

    return lines
