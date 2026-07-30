"""Mock coding interview (~20 min): Refund rules — problem segment only."""


def build():
    d = []

    d.append(("narrator",
        'Coding mock interview. Batch refund processor with rules. Problem segment only. About twenty minutes. The interviewer leaves ambiguity on purpose. No AI.'))

    d.append(("interviewer",
        'Hi. Coding problem, no AI. Implement a batch refund processor. Each refund request has transaction id, amount, currency, reason, merchant id, and request timestamp. Rules you must enforce: cannot refund more than the original payment including prior refunds; cannot continue after fully refunded; merchants have thirty or ninety day windows from purchase; if the original payment used foreign exchange, refunds should use the original rate not a live market rate. Return per item success or failure with a reason. Begin with questions.'))

    d.append(("candidate",
        'Restating. I evaluate each refund against an original payment using ordered rules, independently within a batch. Questions. Are original payments provided as an in memory map from transaction id to payment? Are amounts integers in minor units? Are partial refunds allowed up to remaining balance? First failure reason or all reasons? Is the batch atomic? Do I convert currencies in this segment or keep same currency only?'))

    d.append(("interviewer",
        'Payments map is given. Integer minor units. Partial refunds allowed up to remaining. First failure reason only. Per item independent. Same currency for this segment. Still store original rate on the payment for a later extension.'))

    d.append(("candidate",
        'Naive design is a long chain of if statements inside a loop. It works for four rules and becomes brittle when rules change order or grow. Better design is a Refund Processor that holds ordered rule functions or small rule objects. process batch looks up the payment, runs rules, and mutates refunded amount only after every rule passes. Payment fields: amount, currency, merchant id, purchased at, refunded amount starting at zero, original fx rate defaulting to one. Merchant windows map merchant id to allowed days.'))

    d.append(("interviewer",
        'Walk concrete partial refund scenarios with numbers.'))

    d.append(("candidate",
        'Payment ten thousand cents. Request six thousand on day ten for a thirty day merchant succeeds, refunded becomes six thousand. Request five thousand fails exceeds original remaining. Request four thousand succeeds and fully refunds. Another request fails already fully refunded. A request on day forty fails window expired. Unknown transaction id fails not found. Merchant missing from window map fails closed with unknown policy.'))

    d.append(("interviewer",
        'Why fail closed on unknown merchant?'))

    d.append(("candidate",
        'Refunds move money. If policy is unknown, approving is unsafe. Fail open would silently apply a default I was never given.'))

    d.append(("interviewer",
        'Pseudocode for process batch and apply rules in full words.'))

    d.append(("candidate",
        'Constructor takes payments and merchant windows. Method process batch requests. Results empty list. For each request, payment equals map get transaction id. If missing, append failure original not found and continue. Reason equals apply rules payment request. If reason is not none, append failure with reason and continue. Payment refunded amount increases by request amount. Append success. Method apply rules. If request amount less or equal zero return invalid amount. If currencies differ return currency mismatch. If refunded plus request greater than payment amount return exceeds original. If refunded already greater or equal payment amount return already fully refunded. Window equals windows get merchant id. If window missing return unknown merchant window. If request time minus purchased at exceeds window return window expired. Return none meaning pass. Load bearing: mutate only after pass. Integers only for money.'))

    d.append(("interviewer",
        'Tests?'))

    d.append(("candidate",
        'Partial then partial success. Over remaining. Full then another. Window expired. Unknown id. Unknown merchant. Batch with middle failure still processes neighbors. Zero amount invalid. Clock skew purchase after request invalid.'))

    d.append(("interviewer",
        'New rule: block reason fraud hold. How do you extend?'))

    d.append(("candidate",
        'Add a rule that checks reason against a blocked set and insert it into the ordered list. The batch loop does not change. That is the point of rule objects.'))

    d.append(("interviewer",
        'Where does original F X rate enter later?'))

    d.append(("candidate",
        'When cross currency is allowed, settlement uses stored original rate with explicit rounding. I will not call a live F X service because that would violate the original rate rule.'))

    d.append(("interviewer",
        'Concurrency?'))

    d.append(("candidate",
        'Single threaded in this segment. If concurrent refunds on the same payment are possible, lock per payment id around read rules mutate.'))

    d.append(("interviewer",
        'Complexity?'))

    d.append(("candidate",
        'Time proportional to number of requests times number of rules. Map lookups expected constant. Space for results plus the given payment map.'))

    d.append(("interviewer",
        'Idempotent client retries with the same refund request?'))

    d.append(("candidate",
        'Would need an idempotency key store. Out of scope unless you add it. I mention it as a production follow up so double submits do not double refund.'))

    d.append(("interviewer",
        'What is remaining balance?'))

    d.append(("candidate",
        'Original amount minus refunded amount.'))

    d.append(("interviewer",
        'Difference between exceeds original and fully refunded?'))

    d.append(("candidate",
        'Exceeds means this request would cross the cap. Fully refunded means remaining was already zero.'))

    d.append(("interviewer",
        'How do you store timestamps?'))

    d.append(("candidate",
        'Consistent unix seconds or timezone aware datetimes, never mix naively.'))

    d.append(("interviewer",
        'Should reasons be free text?'))

    d.append(("candidate",
        'Normalize to codes for rules. Free text is for humans.'))

    d.append(("interviewer",
        'What result type do you return?'))

    d.append(("candidate",
        'A list of objects with transaction id, status, and message.'))

    d.append(("interviewer",
        'Can amount be fractional cents?'))

    d.append(("candidate",
        'No. Integer minor units only in this design.'))

    d.append(("interviewer",
        'What if two requests in one batch target the same payment?'))

    d.append(("candidate",
        'Process in order. First may succeed partial, second sees updated refunded amount.'))

    d.append(("interviewer",
        'What is the first test you write?'))

    d.append(("candidate",
        'Exceeds original on a simple fixture.'))

    d.append(("interviewer",
        'How do you avoid float money bugs?'))

    d.append(("candidate",
        'Never use binary float for cash. Integers only.'))

    d.append(("interviewer",
        'What do you say if stuck on rule order?'))

    d.append(("candidate",
        'I propose an order, explain fail closed money safety, and ask if product wants a different priority.'))

    d.append(("interviewer",
        'In live interview you would type the processor next. Offline, implement from blank without AI using the scenarios as tests.'))

    d.append(("candidate",
        'I will implement apply rules and the exceeds and window tests first.'))

    d.append(("interviewer",
        'Let us simulate the implementation phase. Narrate the code you would type in order, as if I am watching your editor. Full words, no silent typing.'))

    d.append(("candidate",
        'I create refunds.py. I define a Payment dataclass or simple class with amount, currency, merchant id, purchased at, refunded amount default zero, original fx rate default one.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I define Refund Request with transaction id, amount, currency, merchant id, request time, reason. I define Result with transaction id, ok bool, message string.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'Class Refund Processor constructor payments dict and merchant windows dict. Method process batch list of requests returns list of results.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'Inside the loop I fetch payment by transaction id. If missing I append Result false original not found and continue. I call reason equals self check payment request. If reason: append Result false reason continue. Then payment refunded amount plus equals request amount. Append Result true ok.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'check method encodes rules in order: amount positive, currency match, exceeds original, already fully refunded, merchant window exists, window not expired. Each failure returns a short stable string code.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I write tests with a payment of ten thousand cents. Partial six thousand then four thousand succeeds. Five thousand after six thousand fails exceeds. Window test uses purchased at and request times. Unknown merchant fails closed.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'If a test mutates on failure, I failed load bearing order and move the mutate line below the checks. I re-run.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I document same currency assumption and stored fx rate for later. Complexity requests times rules. Done for this block.'))

    d.append(("interviewer",
        'Good. Pause. Any compile time or test failure you anticipate?'))

    d.append(("interviewer",
        'Narrate typing the Payment and Result types as if I see your screen.'))

    d.append(("candidate",
        'I define Payment with fields transaction id, amount minor, currency, merchant id, purchased at, refunded amount default zero, original fx rate default one. I define Result with transaction id, success boolean, message string. I keep them boring and explicit.'))

    d.append(("interviewer",
        'Narrate the happy path through process batch with two partial refunds.'))

    d.append(("candidate",
        'Request one arrives for six thousand on a ten thousand payment. Lookup succeeds. Rules all pass. refunded becomes six thousand. Result success. Request two arrives for four thousand. Lookup sees refunded six thousand. exceeds check six thousand plus four thousand equals ten thousand which is allowed. Rules pass. refunded becomes ten thousand. Result success. A third request would fail fully refunded.'))

    d.append(("interviewer",
        'Narrate the failure path for window expiry in the same level of detail.'))

    d.append(("candidate",
        'Lookup succeeds. Amount rules pass. Window map returns thirty days. Request time minus purchased at is forty days. Rule returns window expired. I append failure and I do not touch refunded amount. That non mutation is critical.'))

    d.append(("interviewer",
        'What logging would you add without drowning the interview?'))

    d.append(("candidate",
        'One info log on success with transaction id and amount, one warning on failure with reason code. No card data, no secrets.'))

    d.append(("interviewer",
        'Minute summary to close.'))

    d.append(("candidate",
        'Batch refund processor with ordered rules, first failure reason, integer minor units, partial refunds up to remaining, fail closed unknown merchant, mutate only after pass, original fx rate stored for later cross currency. Tests cover partials, exceeds, window, unknown id, batch independence.'))

    d.append(("interviewer",
        'Why ordered rules instead of independent scoring?'))

    d.append(("candidate",
        'Business wants a deterministic primary reason. First failure is simple and debuggable.'))

    d.append(("interviewer",
        'Could rules be data driven?'))

    d.append(("candidate",
        'Yes later with a rule table. For the session, functions in a list are enough.'))

    d.append(("interviewer",
        'How do you prevent integer overflow?'))

    d.append(("candidate",
        'Language big int in Python helps. In other languages use sixty four bit and validate maxima.'))

    d.append(("interviewer",
        'What is your stance on refund reason free text?'))

    d.append(("candidate",
        'Do not branch on free text. Branch on normalized codes.'))

    d.append(("interviewer",
        'How would you mark a payment refunded in a database?'))

    d.append(("candidate",
        'Update refunded amount where transaction id matches and refunded amount old value matches, optimistic concurrency.'))

    d.append(("interviewer",
        'Why mention optimistic concurrency now?'))

    d.append(("candidate",
        'To show production awareness without implementing a database.'))

    d.append(("interviewer",
        'What is the worst silent bug in this design?'))

    d.append(("candidate",
        'Mutating refunded amount before all rules pass.'))

    d.append(("interviewer",
        'How do you unit test time windows?'))

    d.append(("candidate",
        'Inject purchased at and request time as plain integers in fixtures.'))

    d.append(("interviewer",
        'What if merchant window is zero days?'))

    d.append(("candidate",
        'Only refunds at the exact purchase instant might pass depending on inequality. I would confirm inclusive rules with product.'))

    d.append(("interviewer",
        'First offline coding step?'))

    d.append(("candidate",
        'Fixture payment and test exceeds original.'))

    d.append(("interviewer",
        'Give a continuous five minute implementation monologue as if coding now. I will not interrupt.'))

    d.append(("candidate",
        'I open refunds.py and define Payment and Refund Request with explicit fields and integer amounts. I define Result with success flag and message. I write Refund Processor with payments and windows in the constructor. I write check rules as a single method first to move fast, with a comment that I can split into rule objects if the list grows. Order inside check: validate amount positive, currency match, exceeds original using refunded plus request, fully refunded guard, merchant window lookup fail closed, window expiry comparison. I write process batch to lookup, check, mutate, append results. I create test file with payment ten thousand cents merchant m one window thirty days. I test partial six thousand then four thousand both success and refunded ends at ten thousand. I test five thousand after six thousand fails exceeds and refunded stays six thousand proving non mutation on failure. I test window by setting request time forty days later. I test unknown id and unknown merchant. I run the suite, fix any off by one on window inequality by checking product inclusive rule, and I state the chosen inequality out loud. I add a short docstring on same currency assumption and stored original fx rate. I summarize complexity and stop.'))

    d.append(("interviewer",
        'Confirm the non mutation property again.'))

    d.append(("candidate",
        'If any rule fails, refunded amount is unchanged. Mutation happens only after the full pass. That property prevents partial application of a rejected refund.'))

    d.append(("interviewer",
        'Give the one minute closing summary once more.'))

    d.append(("candidate",
        'This is a batch refund rules engine with ordered checks, first failure reason, integer minor units, partial refunds up to remaining, fail closed merchant policy, and per item independence. Original fx rate is stored for a future cross currency extension without live rates. Tests pin partials, exceeds, window, and batch independence.'))

    d.append(("interviewer",
        'What would you refuse to implement in the remaining minutes even if it sounds impressive?'))

    d.append(("candidate",
        'A general workflow engine, a database mapper, live F X, and machine learning risk scoring. Those are real products, not this problem block. I keep the thin vertical slice working.'))

    d.append(("interviewer",
        'Offline homework remains implement from blank without AI.'))

    d.append(("candidate",
        'Yes. Fixture first, then exceeds and window tests, then process batch.'))

    d.append(("interviewer",
        'I am going to role play a tougher interviewer for a few minutes. I will challenge decisions. Defend them.'))

    d.append(("candidate",
        'Sounds good.'))

    d.append(("interviewer",
        'Why not refund in a database transaction from the start?'))

    d.append(("candidate",
        'Because the exercise is in memory rules. Introducing a database early hides whether I can structure rules and state. I can describe how I would wrap the mutate step in a transaction later without coding SQL now.'))

    d.append(("interviewer",
        'Why integer cents instead of decimal library from the start?'))

    d.append(("candidate",
        'Integers are simple, language portable in explanation, and avoid binary float. A decimal library is fine in production Python, but integer minor units are the standard interview safe choice and match payment systems.'))

    d.append(("interviewer",
        'Your window rule uses which inequality? Defend it.'))

    d.append(("candidate",
        'I will state it explicitly: refund allowed if request time minus purchased at is less than or equal to window days converted to the same unit. That makes the last day inclusive. If product wants exclusive, I flip to less than. The important part is saying the choice and testing the boundary.'))

    d.append(("interviewer",
        'How do you keep the batch independent when two requests hit the same payment?'))

    d.append(("candidate",
        'I process in list order. The first may increase refunded amount. The second sees updated state. That is correct serial semantics for a single threaded batch. I document that order matters.'))

    d.append(("interviewer",
        'Give a second full walkthrough of process batch as if teaching a junior, slower.'))

    d.append(("candidate",
        'Start with an empty results list. Take request one. Find payment. If no payment, fail and move on. Run each rule. If a rule fails, record failure with that reason and do not change payment. If all rules pass, increase refunded amount by the request amount, record success. Take request two and repeat. At the end return all results so the caller can retry failures individually.'))

    d.append(("interviewer",
        'What result fields are mandatory?'))

    d.append(("candidate",
        'Transaction id, success boolean, and a stable message or reason code. Optional: remaining balance after the attempt for easier client debugging.'))

    d.append(("interviewer",
        'Stable reason codes examples?'))

    d.append(("candidate",
        'NOT_FOUND, INVALID_AMOUNT, CURRENCY_MISMATCH, EXCEEDS_ORIGINAL, FULLY_REFUNDED, UNKNOWN_MERCHANT_WINDOW, WINDOW_EXPIRED. Upper snake case keeps logs greppable.'))

    d.append(("interviewer",
        'How would you prevent double processing if the client retries the whole batch?'))

    d.append(("candidate",
        'Idempotency keys per refund request. Without them, retries are dangerous. I call that out as a production requirement even if I do not implement the store in this block.'))

    d.append(("interviewer",
        'Speak a production readiness checklist of five bullets in prose.'))

    d.append(("candidate",
        'One integer money. Two deterministic reasons. Three non mutation on failure. Four explicit window policy. Five tests for partials exceeds window and unknown merchant. Bonus: concurrency plan and idempotency plan spoken as follow ups.'))

    d.append(("interviewer",
        'Closing challenge: what is the single most important line in your code?'))

    d.append(("candidate",
        'The line that increases refunded amount, because it must sit after every rule passes. Everything else supports that safe mutation.'))

    d.append(("narrator",
        'Speed recap. Ordered rules. First reason. Mutate only on pass. Integer money. Partial allowed. Fail closed unknown merchant. Shadow then code AI off.'))

    return d
