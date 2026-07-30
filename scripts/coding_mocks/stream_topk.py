"""Mock coding interview (~20 min): Stream top-K — problem segment only."""


def build():
    d = []

    d.append(("narrator",
        'Coding mock interview. Stream top K types and moving average. Problem segment only. About twenty minutes. Two voices. No AI.'))

    d.append(("interviewer",
        'Hi. No AI in this block. You will process a stream of transactions. Each event has a type string and an integer amount. Build a class that ingests events one by one, answers top K types by frequency so far, and answers the moving average of amounts over the last N events. Prefer efficient updates. Clarify first.'))

    d.append(("candidate",
        'Restating. Online ingest. Exact global frequency top K. Moving average over a trailing count window of N amounts. Questions. How are ties broken? Negative amounts allowed? Is N count based or time based? Is K fixed at construction or passed per query? Single threaded? Exact or approximate?'))

    d.append(("interviewer",
        'Ties broken by type string ascending. Reject negatives. N is event count fixed at construction. K passed per query. Single threaded. Exact counts.'))

    d.append(("candidate",
        'Naive top K stores all events and rescans each query, linear in stream length. Better: hash map type to count, update on process in expected constant time. Top K query sorts entries by count descending then type ascending and takes the first K. Moving average uses a deque of the last N amounts plus a running sum so process and average are constant time. On process, if deque length equals N, subtract the leftmost amount from the sum and pop left, then append the new amount and add it to the sum.'))

    d.append(("interviewer",
        'Hand walk average with N three and amounts ten, twenty, thirty, forty.'))

    d.append(("candidate",
        'After ten average ten. After twenty average fifteen. After thirty average twenty. After forty drop ten, window twenty thirty forty, sum ninety, average thirty.'))

    d.append(("interviewer",
        'Hand walk types pay, pay, refund, pay, fee with K two.'))

    d.append(("candidate",
        'Counts pay three, refund one, fee one. Top is pay, then fee before refund by ascending type among ties.'))

    d.append(("interviewer",
        'Pseudocode in full words for process, top K, and moving average.'))

    d.append(("candidate",
        'Class Stream Analytics. Constructor window size N greater than zero. Fields counts map, deque amounts, running sum. Method process type amount. Reject negative amount. Reject empty type. Counts type plus one. If deque length equals N, running sum minus equals pop left. Append amount, running sum plus equals amount. Method top K. If K less or equal zero return empty list. Sort count items by negative count then type string. Return first min K and number of types. Method moving average. If deque empty raise empty stream. Return running sum divided by length. Load bearing: subtract before pop. Deterministic ties.'))

    d.append(("interviewer",
        'Complexity?'))

    d.append(("candidate",
        'Process expected O of one. Top K query O of U log U for U distinct types. Space O of U plus N.'))

    d.append(("interviewer",
        'When would you not sort all types on query?'))

    d.append(("candidate",
        'If U is huge and top K queries are extremely hot, I would discuss better structures. For typical interview scale, map plus sort is clear and honest. I will not half implement a fancy heap without a full plan.'))

    d.append(("interviewer",
        'What if K exceeds distinct types?'))

    d.append(("candidate",
        'Return all types in sorted order.'))

    d.append(("interviewer",
        'What if N is one?'))

    d.append(("candidate",
        'Average is always the latest amount.'))

    d.append(("interviewer",
        'What if amount is zero?'))

    d.append(("candidate",
        'I allow zero unless product forbids.'))

    d.append(("interviewer",
        'Empty stream top K?'))

    d.append(("candidate",
        'Empty list.'))

    d.append(("interviewer",
        'Empty stream average?'))

    d.append(("candidate",
        'Raise or return none. I raise for clarity.'))

    d.append(("interviewer",
        'Thread safety?'))

    d.append(("candidate",
        'Single threaded now. Would lock across process and queries later.'))

    d.append(("interviewer",
        'Why deterministic ties?'))

    d.append(("candidate",
        'So tests and API clients do not see flicker among equals.'))

    d.append(("interviewer",
        'ML framing sentence?'))

    d.append(("candidate",
        'Like counting tool call types and a short window average of usage.'))

    d.append(("interviewer",
        'Reset for tests?'))

    d.append(("candidate",
        'Clear method empties map, deque, and sum.'))

    d.append(("interviewer",
        'Float average concerns for money?'))

    d.append(("candidate",
        'Keep integer sum; document float division or use decimal.'))

    d.append(("interviewer",
        'Invalid N?'))

    d.append(("candidate",
        'Constructor raises if N less or equal zero.'))

    d.append(("interviewer",
        'Empty type string?'))

    d.append(("candidate",
        'Reject as invalid event.'))

    d.append(("interviewer",
        'Live you would implement next. Offline, code from blank without AI using the hand walks as tests.'))

    d.append(("candidate",
        'Average tests first, then top K ties, then process validation.'))

    d.append(("interviewer",
        'Let us simulate the implementation phase. Narrate the code you would type in order, as if I am watching your editor. Full words, no silent typing.'))

    d.append(("candidate",
        'I create stream_analytics.py. From collections import deque and Counter or a plain dict. Class Stream Analytics constructor window size N. If N less or equal zero raise. Self counts dict, self window deque, self running sum zero, self N equals N.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'Method process type amount. If amount less than zero raise. If type is empty raise. Counts type equals counts get type zero plus one. If length of window equals N: old equals pop left, running sum minus equals old. Window append amount, running sum plus equals amount.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'Method top K. If K less or equal zero return empty list. Items equals list counts items. Items sort key lambda pair: negative pair count, pair type. Return list of types for first min K and length items.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'Method moving average. If not window raise empty. Return running sum divided by length of window as float.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'Tests: average walk ten twenty thirty forty with N three expects thirty at end. Top K example pay pay refund pay fee expects pay then fee. Empty average raises. Negative process raises.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'If average drifts I forgot subtract on pop. If top K flicker among ties I check secondary key. I re-run tests until green and state complexity.'))

    d.append(("interviewer",
        'Good. Pause. Any compile time or test failure you anticipate?'))

    d.append(("interviewer",
        'Narrate writing process as if typing each line.'))

    d.append(("candidate",
        'Def process self type amount. If amount less than zero raise Value Error. If not type raise Value Error. Self counts type equals self counts get type zero plus one. If len self window equals self N: old equals self window pop left, self running sum minus equals old. Self window append amount. Self running sum plus equals amount.'))

    d.append(("interviewer",
        'Narrate top K the same way.'))

    d.append(("candidate",
        'Def top K self k. If k less or equal zero return empty list. Items equals list self counts items. Items sort with key lambda item: minus item one, item zero. Return list of item zero for item in items slice min k and length.'))

    d.append(("interviewer",
        'Narrate moving average.'))

    d.append(("candidate",
        'Def moving average self. If not self window raise Empty Stream Error. Return self running sum divided by len self window.'))

    d.append(("interviewer",
        'Walk a full test file outline.'))

    d.append(("candidate",
        'test average walk, test top K ties, test empty average raises, test negative rejects, test k zero returns empty, test k larger than distinct returns all, test N one average tracks latest.'))

    d.append(("interviewer",
        'Minute summary.'))

    d.append(("candidate",
        'Stream analytics with frequency map for exact top K and deque plus running sum for last N average. Deterministic ties. Reject negatives. Process expected constant time. Top K query U log U. Space U plus N.'))

    d.append(("interviewer",
        'Why not store timestamps if N is time based later?'))

    d.append(("candidate",
        'This problem is count based. Time based needs a different window structure. I would redesign if requirements change.'))

    d.append(("interviewer",
        'Can counts go down?'))

    d.append(("candidate",
        'Not in this problem. If events can be revoked I would need decrement logic.'))

    d.append(("interviewer",
        'How do you avoid float sum error on averages?'))

    d.append(("candidate",
        'For money keep integer sum and define average policy. For interview float division is usually accepted if documented.'))

    d.append(("interviewer",
        'What if type cardinality explodes?'))

    d.append(("candidate",
        'Memory grows with U. Production might need eviction or approximation. Out of scope unless asked.'))

    d.append(("interviewer",
        'Is Counter better than dict?'))

    d.append(("candidate",
        'Either fine. Counter is convenient. Dict is explicit.'))

    d.append(("interviewer",
        'How do you explain deque to a junior?'))

    d.append(("candidate",
        'A list optimized for pop from left so the oldest amount leaves efficiently.'))

    d.append(("interviewer",
        'What breaks if you forget running sum?'))

    d.append(("candidate",
        'You might re-sum each time O of N or worse drift if you update wrong.'))

    d.append(("interviewer",
        'First offline test?'))

    d.append(("candidate",
        'Average walk with N three.'))

    d.append(("interviewer",
        'Second offline test?'))

    d.append(("candidate",
        'Top K ties with pay refund fee.'))

    d.append(("interviewer",
        'When do you stop coding?'))

    d.append(("candidate",
        'When tests for average, top K, and validation are green and complexity is stated.'))

    d.append(("interviewer",
        'Continuous implementation monologue for about five minutes. Speak the code and tests.'))

    d.append(("candidate",
        'I create stream_analytics.py and import deque. Constructor stores N, empty counts dict, empty deque, running sum zero, with validation N positive. process updates counts, maintains the window with subtract on pop left, then append and add. top K sorts by negative count and type, slices K. moving average divides running sum by length or raises if empty. I write test average walk expecting ten, fifteen, twenty, thirty across steps if I assert intermediate values, or at least final thirty. I write test top K on pay pay refund pay fee expecting pay then fee. I write test negative amount raises, empty type raises, k zero returns empty, empty average raises. I run pytest, fix any bug where I pop without subtract, which is the classic window bug. I restate complexity and production follow ups time windows and concurrency, without coding them.'))

    d.append(("interviewer",
        'Repeat the classic window bug and the fix.'))

    d.append(("candidate",
        'The classic bug is popping the oldest amount without subtracting it from the running sum, or subtracting the wrong value. The fix is always subtract the value you remove, then remove it, then add the new value to both deque and sum.'))

    d.append(("interviewer",
        'Repeat the top K tie break rule.'))

    d.append(("candidate",
        'Higher count wins. If counts are equal, the type string that sorts ascending comes first, so fee before refund when both have count one.'))

    d.append(("interviewer",
        'One minute closing summary.'))

    d.append(("candidate",
        'Stream analytics with a frequency map for exact top K queries and a deque plus running sum for the last N amounts average. Validation rejects negative amounts and empty types. Process is expected constant time, top K is U log U, space is U plus N. This matches monitoring style metrics for agent platforms while remaining a pure coding exercise.'))

    d.append(("interviewer",
        'What will you implement first offline?'))

    d.append(("candidate",
        'The moving average window invariant tests, because they catch sum drift quickly, then top K ties, then validation.'))

    d.append(("interviewer",
        'Good. That ends the problem block.'))

    d.append(("candidate",
        'Thank you. I will code it from blank without AI next.'))

    d.append(("interviewer",
        'Tougher probe section. Defend design choices.'))

    d.append(("candidate",
        'Ready.'))

    d.append(("interviewer",
        'Why not a fixed array of size N for the window?'))

    d.append(("candidate",
        'A circular array is a valid optimization. Deque communicates intent clearly in an interview and is hard to get wrong for pop left. If performance matters I can switch to circular indices later without changing the sum invariant.'))

    d.append(("interviewer",
        'Why sort all types rather than maintain a live top K heap?'))

    d.append(("candidate",
        'A live heap of size K is subtle when counts change for many keys because you need to know whether a type is already in the heap and how to update. For exact answers with moderate U, sorting on query is simpler and less bug prone. I choose clarity first.'))

    d.append(("interviewer",
        'Give a junior-friendly explanation of the running sum invariant.'))

    d.append(("candidate",
        'The running sum always equals the sum of amounts currently in the window deque. When an amount enters, add it to both. When an amount leaves, subtract it from the sum and remove it from the deque. If that invariant holds, average is sum divided by length.'))

    d.append(("interviewer",
        'Walk a bug scenario where you subtract after pop incorrectly.'))

    d.append(("candidate",
        'If I pop first and lose the value, I cannot subtract the correct old amount. Sum becomes too large, averages drift upward, and tests on the ten twenty thirty forty sequence fail by ending above thirty.'))

    d.append(("interviewer",
        'How do you make top K output stable in tests?'))

    d.append(("candidate",
        'Secondary sort key on type ascending. Even when counts tie, the order is deterministic across runs and languages that have stable sorts.'))

    d.append(("interviewer",
        'What happens if process is called with amount none or null?'))

    d.append(("candidate",
        'I treat it as invalid input and raise a type or value error. I do not coerce silently.'))

    d.append(("interviewer",
        'Speak a five item production checklist in prose.'))

    d.append(("candidate",
        'One validate inputs. Two keep sum invariant. Three deterministic top K. Four metrics on process rate. Five concurrency strategy if multi threaded ingest appears. Approximation only if cardinality explodes.'))

    d.append(("interviewer",
        'Full closing summary one more time, interview voice.'))

    d.append(("candidate",
        'I built stream analytics with a hash map of exact frequencies for top K queries and a deque backed moving average over the last N amounts using a running sum. Process is expected constant time. Top K is U log U. Space is U plus N. Negatives and empty types are rejected. Ties break by type name. This is the thin solution I would implement in the editor next.'))

    d.append(("interviewer",
        'What is the first keystroke offline?'))

    d.append(("candidate",
        'Class skeleton and the average walk test expectations.'))

    d.append(("interviewer",
        'One more full teach-back. Explain the entire design to a new teammate who will implement it tomorrow. Take your time.'))

    d.append(("candidate",
        'We need two features on a stream of typed amounts. First, exact top K frequent types. Second, average of the last N amounts. I would use a dictionary from type to count. Every process increments the count for that type. For top K I copy the dictionary entries, sort by higher count first and by type name when counts match, then take K names. For the average I keep a deque of amounts and a running sum. When the deque already has N amounts I remove the oldest amount from the left and subtract it from the sum, then I append the new amount and add it to the sum. Average is sum divided by how many amounts are currently stored, which can be less than N at the beginning of the stream. I reject negative amounts and empty types. I do not use AI in the coding segment. Complexity is constant time expected for process and U log U for top K if U is the number of distinct types. Space is U plus N. The main bug to avoid is breaking the running sum when the window slides. The main product framing is monitoring like metrics for agent tool calls and usage.'))

    d.append(("interviewer",
        'Perfect. That is the level of clarity I want in the interview room.'))

    d.append(("candidate",
        'Thank you. I will implement it from a blank file without AI after this.'))

    d.append(("interviewer",
        'Let us do one final full mock exchange as if we restarted the last third of the problem. I ask: implement moving average carefully. You answer with pseudocode and a test plan only.'))

    d.append(("candidate",
        'I keep a deque of amounts and a running sum. Constructor fixes N. On process, if the deque already holds N amounts, I read the leftmost amount, subtract it from the running sum, pop left, then append the new amount and add it to the sum. Moving average returns running sum divided by current length, or raises if the deque is empty. Tests: N three with amounts ten twenty thirty forty expects intermediate averages ten fifteen twenty and final thirty. Another test N one expects average always equal to the latest amount. A third test empty average raises before any process call.'))

    d.append(("interviewer",
        'Now the top K third. Pseudocode and tests only.'))

    d.append(("candidate",
        'Counts map updates on process. top K copies items, sorts by higher count first and by type name ascending on ties, returns the first K type names or all if fewer than K types exist. Tests: the pay pay refund pay fee stream with K two expects pay then fee. K zero returns empty. K one hundred returns all three types in order pay fee refund.'))

    d.append(("interviewer",
        'Combine both into one spoken acceptance checklist.'))

    d.append(("candidate",
        'Process accepts valid events and rejects negatives and empty types. Average matches the hand walk. Top K matches the hand walk and tie break. Complexity spoken. No AI used. Code is ready for screen share implementation.'))

    d.append(("interviewer",
        'Excellent. End of problem block.'))

    d.append(("candidate",
        'Thank you.'))

    d.append(("narrator",
        'Speed recap. Map counts. Sort top K with ties. Deque plus running sum. Reject negatives. Shadow then code AI off.'))

    return d
