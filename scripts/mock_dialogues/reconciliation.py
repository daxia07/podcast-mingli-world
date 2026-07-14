"""Mock Interview: Bank & Partner Reconciliation — Two-voice dialogue."""


def build():
    lines = []

    # SECTION 1: Requirements
    lines.append(("interviewer", "Hi, welcome. Today I'd like you to design a reconciliation system for a global payments platform. Payments are sent to many banks and local rails. Callbacks can be missing, duplicated, late, or contradictory. Banks also provide daily statements with different formats and cut-off times. The system must prove the platform's internal ledger agrees with external bank positions, find discrepancies quickly, support operations investigation, and post safe repairs. Assume fifty partners, millions of transactions per day, and zero tolerance for unexplained money differences."))

    lines.append(("candidate", "Thanks. Reconciliation is the immune system of a financial platform — it detects when something is wrong and triggers the right response. Most people think of it as a nightly batch report, but I'd design it as a continuous control system. Let me clarify the requirements. First, what types of reconciliation do we need? Transaction-level matching, aggregate balance reconciliation, or both?"))

    lines.append(("interviewer", "Both. Transaction-level matching for day-to-day operations — matching each payment to its bank confirmation. Aggregate balance reconciliation for end-of-day control — proving that the total of all internal ledger positions equals the bank's reported position."))

    lines.append(("candidate", "Second question: what are the sources of external evidence? Real-time callbacks, periodic API status pulls, daily statement files, or all of the above?"))

    lines.append(("interviewer", "All of the above. Some partners send real-time webhooks when a payment settles. Some require us to poll their API. Most provide daily statement files in various formats — MT940, BAI2, CSV, or proprietary. The statement file is typically the final authoritative source."))

    lines.append(("candidate", "Third question: what's the cadence? Real-time matching as callbacks arrive, nightly batch matching against statements, or a hybrid?"))

    lines.append(("interviewer", "Hybrid. Intraday matching as callbacks and API pulls come in, end-of-day reconciliation against statement files. The intraday matching reduces risk exposure — we catch discrepancies sooner. The end-of-day reconciliation is the final control."))

    lines.append(("candidate", "Clear. Summary: continuous control system, transaction-level plus aggregate reconciliation, multiple evidence sources with statement files as authoritative, intraday matching plus end-of-day control, fifty partners, millions of transactions, zero tolerance for unexplained differences. Moving to architecture."))

    # SECTION 2: Architecture
    lines.append(("interviewer", "Show me the architecture."))

    lines.append(("candidate", "The reconciliation pipeline has four stages. Stage one: ingestion. Partner callbacks, API status pulls, and statement files are ingested into a raw immutable store. Every piece of external evidence is preserved in its original form — the raw webhook payload, the API response, the statement file — along with metadata like received time, source, and checksum. Ingestion is idempotent: if the same callback or file is delivered twice, we detect the duplicate by source, file ID, and checksum, and skip it. We never silently drop data."))

    lines.append(("candidate", "Stage two: normalization. A parser converts each raw record into a normalized internal format — partner ID, partner transaction ID, our instruction ID if available, currency, signed amount, fees, value date, booking date, account, and status. Each partner has its own parser with a version number, because formats differ and change. Parser versions are auditable — if a parser bug causes a matching failure, we can reparse historical files with the corrected version."))

    lines.append(("candidate", "Stage three: matching. The match engine compares normalized external records against internal payment, instruction, and ledger data. It uses stable references first — our instruction ID or the end-to-end reference that we sent to the bank. These create high-confidence exact matches. For unmatched records, it builds candidate sets by corridor, amount, currency, account, and value-date window, and scores them. It never automatically chooses an ambiguous match — ambiguous cases go to the exception queue for human review."))

    lines.append(("candidate", "Stage four: exception handling and repair. The match engine classifies each record as: exact settled match, expected timing difference, returned or chargeback, duplicate external record, duplicate internal instruction, amount or fee discrepancy, or unknown external movement. Each exception becomes a durable case with evidence, state, priority by monetary value and age, owner, and immutable resolution reason. Approved repairs generate separate adjustment or return journals and new reconciliation links. They never overwrite a source record."))

    # SECTION 3: Deep Dive — Matching Algorithm
    lines.append(("interviewer", "Walk me through the matching algorithm in detail. How do you handle the case where stable references aren't available?"))

    lines.append(("candidate", "The matching algorithm runs in phases. Phase one: deduplication. Before matching, we deduplicate exact records by partner, file, row, and partner transaction ID. Banks sometimes send duplicate entries in statement files, and callbacks can be delivered multiple times. Duplicate detection prevents false exceptions."))

    lines.append(("candidate", "Phase two: exact match by stable reference. We have our internal instruction ID, and when we sent the payment to the bank, we included this ID as the end-to-end reference or the remittance information. When the bank's callback or statement includes this reference, we match directly. This is the highest-confidence match — it's deterministic, no ambiguity. About seventy to eighty percent of records match this way for well-integrated partners."))

    lines.append(("candidate", "Phase three: candidate matching for unmatched records. For the remaining twenty to thirty percent — where the bank didn't return our reference, or the reference was truncated or garbled — we build candidate sets. A candidate set is all internal records that could potentially match this external record, filtered by: same partner, same currency, same account, amount within a tolerance — because banks sometimes net fees or split transactions, and value date within a window — typically plus or minus three business days, because settlement timing varies. We score candidates by the number of matching attributes and the closeness of amounts and dates."))

    lines.append(("candidate", "Phase four: classification. If exactly one candidate has a high score — say above ninety percent confidence — we classify it as a probable match and auto-match it, but flag it for review. If multiple candidates have similar scores, we classify it as ambiguous and send it to the exception queue. If no candidates exist, we classify it as unknown external movement — a transaction on the bank statement that we didn't initiate. This could be a bank fee, an interest payment, or a fraudulent transaction. It always goes to the exception queue."))

    lines.append(("candidate", "The critical rule: never automatically choose an ambiguous match. A wrong match is worse than an unmatched record. An unmatched record sits in the exception queue and gets investigated. A wrong match hides a real discrepancy that could represent lost or stolen money."))

    # SECTION 4: Deep Dive — Aggregate Control
    lines.append(("interviewer", "How does aggregate balance reconciliation work? Even if every transaction matches, the totals might not agree."))

    lines.append(("candidate", "Aggregate control is the safety net that catches what transaction-level matching misses. For each partner account and currency, we compute: opening balance plus all debits minus all credits equals closing balance. We do this for both our internal ledger view and the bank's statement view. If they agree — opening balances match, closing balances match — then even if a few individual transactions are mismatched, the overall position is correct. If they disagree, there's a break — a control account difference — that must be investigated."))

    lines.append(("candidate", "A perfect row-level match does not replace this control. Why? Because there could be transactions on the bank statement that don't match any internal record — bank fees, interest, adjustments — that would be missed if we only matched row by row. The aggregate check catches these. And conversely, the aggregate check doesn't tell you which specific transaction is wrong — that's what row-level matching is for. They're complementary."))

    lines.append(("candidate", "We run the aggregate check at end of day, after the statement file is processed. If there's a break, it's escalated immediately. The operations team investigates: is it a timing difference — our ledger posted today but the bank posts tomorrow? Is it a missing transaction? Is it an amount discrepancy? The break is tracked until resolved, with SLAs — a break over a certain monetary threshold must be investigated within four hours."))

    # SECTION 5: Failure Scenarios
    lines.append(("interviewer", "What happens when a statement file is delayed?"))

    lines.append(("candidate", "A delayed statement file means we can't complete end-of-day reconciliation for that partner. We mark the expected feed as late and alert the owner — someone in operations who is responsible for that partner relationship. In the meantime, all payments to that partner are classified as timing differences — they're not exceptions, they're expected settlements that haven't been confirmed yet. We avoid taking any repair actions based on the absence of a statement — no premature adjustments. When the file arrives, possibly the next day, we process it normally. Late files are common in banking — some partners are consistently late, and we adjust our SLAs accordingly."))

    lines.append(("interviewer", "A bank response to a payment timed out. How does reconciliation handle this?"))

    lines.append(("candidate", "The payment is in submission unknown state — we sent the instruction but don't know if the bank received it. This is exactly the scenario where reconciliation proves its value. The payment stays in submission unknown until one of three things provides evidence: a callback confirming settlement, a status API pull showing the bank's record, or the end-of-day statement showing the credit to the beneficiary. Any of these resolves the uncertainty. If none of them appear — the payment isn't in the callback, the API shows no record, and the statement doesn't include it — we can safely conclude the bank didn't process it and mark it as failed. The key principle: a timeout is unknown, not failed. We query, reconcile, or repair before retrying."))

    lines.append(("interviewer", "The partner changes their file format without telling us."))

    lines.append(("candidate", "Format changes are a recurring operational challenge. Our defense: parser contract tests. Each partner's parser has a set of test cases based on real files we've received. When we receive a new file, we detect its format version — there's usually a header field or a structural signature. If the format doesn't match any known version, we quarantine the file — don't process it, don't silently drop rows. We alert the operations team, who investigates and either updates the parser or contacts the partner. Quarantined files are retained for reprocessing once the parser is updated. This is why we store raw files immutably — reprocessing is always safe."))

    # SECTION 6: Metrics and Operations
    lines.append(("interviewer", "What metrics do you monitor for the reconciliation system?"))

    lines.append(("candidate", "Seven key metrics. One: reconciled count and value — what percentage of transactions are matched. Two: unmatched count and value by ageing bucket — how many exceptions exist and how old they are. Exceptions that age beyond their SLA are escalated. Three: control-account break amount — the aggregate difference between our ledger and bank statements. Four: feed freshness — when did we last receive data from each partner. Late feeds are flagged. Five: auto-match rate — what percentage of records match automatically without human intervention. This should be above ninety-five percent for well-integrated partners. Six: exception SLA — how quickly exceptions are resolved. Seven: repair volume — how often we're posting correcting journals. High repair volume indicates a systemic issue that needs root-causing, not more repairs."))

    # SECTION 7: Summary with Killer Phrases
    lines.append(("candidate", "Let me close with the killer phrases for reconciliation. One: reconciliation is a control system, not a report — it's continuous, not just nightly. Two: preserve raw evidence immutably — files, callbacks, API responses, with checksums and parser versions. Three: exact references first, fuzzy candidates second — never auto-choose an ambiguous match. Four: a wrong match is worse than an unmatched record — exceptions surface discrepancies, wrong matches hide them. Five: aggregate control catches what row-level matching misses — opening plus movements must equal closing, for both internal and external views. Six: a timeout is unknown, not failed — query, reconcile, or repair before retrying. Seven: repairs are compensating journals, never edits — the original record is immutable, the repair is a new entry with an approval trail. Eight: quarantine unknown formats, never silently drop rows — parser contract tests and version detection protect against format changes. The phrase to remember: reconciliation is a control system, not a report."))

    lines.append(("interviewer", "Walk me through a complete reconciliation cycle for a day."))

    lines.append(("candidate", "Morning: the previous day's statement files start arriving. Each file is ingested — checksum verified, raw file stored, parser applied. The normalization converts bank-specific records into our internal format. For a major Australian bank partner, the MT940 file contains fifteen hundred transactions. The parser extracts opening balance, individual transaction lines with amounts, references, and value dates, and closing balance."))

    lines.append(("candidate", "Matching runs. Phase one: twelve hundred records match exactly by our end-to-end reference — we included it in the payment instruction, and the bank returned it. Phase two: two hundred records match by candidate scoring — same currency, same account, amount within tolerance, value date within window. Ten of these are flagged as probable matches for review. Phase three: one hundred records remain unmatched. Ninety are timing differences — payments we sent today that will appear in tomorrow's statement. Ten are exceptions — two bank fees with no corresponding internal record, three amount discrepancies where the bank's amount differs from ours, and five unknown external credits."))

    lines.append(("candidate", "Aggregate control runs. Opening balance from the statement: five million AUD. Our internal opening balance: five million AUD. They match. Closing balance from statement: four point eight two million AUD. Our internal closing balance: four point eight one five million AUD. Break of five thousand AUD. This is the aggregate signal that something is wrong, even though most transactions matched individually. The break is escalated. Investigation reveals: the five unknown external credits total five thousand AUD — they're incoming transfers from other banks that our system hasn't processed yet because they bypassed the normal payment flow. Operations creates receiving journals for these credits, and the break is resolved."))

    lines.append(("candidate", "End of day: all breaks resolved, all exceptions triaged, repair journals posted with approval trails. The daily reconciliation report shows: fifteen hundred records processed, fourteen hundred auto-matched, ten probable matches confirmed, ninety timing differences, ten exceptions resolved, zero unexplained breaks. The platform's internal ledger agrees with every partner's position. No money lost, no money created, no money unexplained. Reconciliation is a control system, not a report."))

    return lines
