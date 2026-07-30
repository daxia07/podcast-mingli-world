"""Mock coding interview (~20 min): FX anomaly detector — sliding window average."""


def build():
    d = []

    d.append(("narrator",
        'This is a coding mock interview focused only on the problem block. About twenty minutes of two voice dialogue. No AI tools. Ear only first. Pause on second play. Shadow on third.'))

    d.append(("interviewer",
        'Hi, thanks for coming in. One coding problem. Python fine. No AI. Clarify, design, hand walk, pseudocode, corners, complexity. Ready?'))

    d.append(("candidate",
        'Yes. Please go ahead.'))

    d.append(("interviewer",
        'Here is the problem, framed like a historical take home style task. You process a stream of foreign exchange ticks. Each tick has a timestamp in seconds, a currency pair string like U S D to A U D, and a mid rate as a float. I need an anomaly detector that flags a tick when the current rate differs from the recent moving average of the same pair by at least ten percent. The moving average is over a five minute window of ticks for that pair ending at the current tick time. Functional requirements: process ticks online, return whether each tick is anomalous, keep the design clear for multiple pairs. Non functional: honest complexity and tests with fixed timestamps. What questions do you have?'))

    d.append(("candidate",
        'Restating. Per currency pair, maintain rates in a time window of five minutes. For each new tick, update that pair window, compute the average of rates still in the window, and flag if absolute rate minus average over average is at least zero point one, careful when average is zero. Clarifying questions. Is the window closed on the left as now minus three hundred seconds exclusive or inclusive? Does the current tick itself count inside the average before the check, or do we compare against the average of previous ticks only? Are timestamps non decreasing globally or only per pair? Can timestamps be equal? Float rates may be zero or negative? Should I return a boolean list aligned with inputs, or a list of anomaly event objects? In memory only? Single threaded?'))

    d.append(("interviewer",
        'Good questions. Window is the last five minutes inclusive of the current tick after you add it, unless you argue why previous only is better. Prefer non decreasing timestamps per pair; if a tick is older than the last for that pair, either ignore or error, state your choice. Equal timestamps allowed. Rates are positive for this cut. Return a boolean for each processed tick. In memory, single threaded. Five minutes is three hundred seconds. Threshold ten percent is configurable if easy.'))

    d.append(("candidate",
        'Naive approach. Store all historical ticks, on each event filter last five minutes by scan, average, compare. Correct but O of history per tick. Better. Per pair keep a deque of timestamp and rate pairs, and running sum of rates in the window. On new tick, append, add rate to sum, pop left while front timestamp is less than now minus three hundred, subtract popped rates from sum. Average equals sum divided by count. Anomaly if count is at least one and absolute rate minus average divided by average is greater than or equal to threshold. Using inclusive current tick means a single first tick averages to itself and is never a ten percent anomaly against itself, which is reasonable cold start. Product framing: FX ops and risk style monitoring for sudden dislocations on a pair, similar spirit to stream features without claiming a full trading system.'))

    d.append(("interviewer",
        'Why deque plus running sum instead of recomputing average each time?'))

    d.append(("candidate",
        'Amortized O of one updates if timestamps are roughly ordered: each tick enters and leaves the deque once. Recomputing sum each time is O of window length per tick, which can be large under high frequency quotes. Running sum keeps average O of one after eviction loop.'))

    d.append(("interviewer",
        'Hand walk one pair. Threshold ten percent. Window three hundred seconds. Ticks: t zero rate one point zero, t ten rate one point zero, t twenty rate one point two. Speak window contents and decisions.'))

    d.append(("candidate",
        'First tick t zero rate one. Window one tick, average one, deviation zero, not anomaly. Second t ten rate one. Window two ticks sum two average one, deviation zero, not anomaly. Third t twenty rate one point two. Window three ticks sum three point two average about one point zero six seven. Absolute one point two minus average over average is roughly twelve point five percent, which is greater than or equal to ten percent, flag anomaly true. If the interviewer wanted previous only average, the average would be one and deviation twenty percent, also anomaly. I stick to inclusive window as agreed and document cold start.'))

    d.append(("interviewer",
        'Hand walk eviction. After many ticks, a tick at t equals four hundred with rate one, while old ticks at t zero still in structure if you forgot to pop.'))

    d.append(("candidate",
        'On the tick at four hundred, I pop left while front timestamp less than four hundred minus three hundred equals one hundred. So t zero leaves if it is still present. Sum decreases by removed rates. If I forget eviction, the average is polluted by ancient prices and anomalies become meaningless. Eviction is load bearing.'))

    d.append(("interviewer",
        'Describe the class API.'))

    d.append(("candidate",
        'Class F X Anomaly Detector. Constructor takes window seconds default three hundred and threshold default zero point one. Internal map from pair string to a small state of deque and running sum. Method observe pair, timestamp, rate returns bool is anomaly. Optional method observe tick object. I validate rate greater than zero and window positive at construction.'))

    d.append(("interviewer",
        'Full word pseudocode for observe.'))

    d.append(("candidate",
        'Method observe pair timestamp rate. If rate is less than or equal to zero raise. State equals map get or create empty deque and sum zero for pair. If state last timestamp exists and timestamp is less than last, raise out of order or skip per policy; I will raise for clarity. Append timestamp rate to deque, sum plus equals rate, last equals timestamp. While deque and deque left timestamp less than timestamp minus window seconds: old t old r equals pop left, sum minus equals old r. Count equals length deque. Average equals sum divided by count. Deviation equals absolute rate minus average divided by average. Return deviation greater than or equal to threshold. Load bearing: evict before decision after adding current. Load bearing: per pair isolation. Load bearing: avoid divide by zero count, but count at least one after append.'))

    d.append(("interviewer",
        'What if the window is so short or ticks so sparse that only one tick remains?'))

    d.append(("candidate",
        'Average equals that tick, deviation zero, not anomaly. That is acceptable cold start. If product wants anomaly versus a longer baseline, that is a different feature, not this five minute average.'))

    d.append(("interviewer",
        'Corners and tests.'))

    d.append(("candidate",
        'First tick false. Steady rates false. Jump of ten percent true. Jump of nine percent false. Two pairs do not share windows. Eviction removes old influence. Out of order raises. Rate zero raises. Threshold boundary exactly ten percent true with greater or equal. Empty no observe. Fake timestamps in tests, no sleeps.'))

    d.append(("interviewer",
        'Complexity?'))

    d.append(("candidate",
        'Amortized O of one per tick for ordered input because each tick enters and leaves once. Worst case a single observe can pop many expired ticks, still amortized linear over the stream. Space O of ticks inside windows across pairs.'))

    d.append(("interviewer",
        'I extend: also require minimum count of five ticks in the window before flagging. How?'))

    d.append(("candidate",
        'After eviction, if count less than five return false without checking threshold. One guard. Structure same. Product often wants this to avoid noisy flags on thin markets.'))

    d.append(("interviewer",
        'I extend: detect anomaly if either last price or average moves more than ten percent versus the average five minutes ago, not versus current average. What changes?'))

    d.append(("candidate",
        'That needs a delayed baseline, maybe a second structure or store average snapshots. Larger change. I would restate the metric carefully and not pretend it is the same one liner. For this interview I keep current rate versus current window average unless you insist on the variant.'))

    d.append(("interviewer",
        'Float precision issues?'))

    d.append(("candidate",
        'For interview floats are fine with a threshold compare. Production FX may use decimals and tick size. I would not over engineer decimal here unless asked, but I avoid equality checks on floats except via the threshold inequality.'))

    d.append(("interviewer",
        'Simulate implementation narration.'))

    d.append(("candidate",
        'I write class with window and threshold, defaultdict or dict of pair to deque and sum and last timestamp. observe appends, evicts, averages, returns boolean. Tests with fixed times for steady, jump, eviction, multi pair.'))

    d.append(("interviewer",
        'Continue.'))

    d.append(("candidate",
        'If a test fails because average includes too much history, I fix the while eviction condition. If pairs leak, I verify map keying by pair string.'))

    d.append(("interviewer",
        'One minute summary.'))

    d.append(("candidate",
        'FX anomaly detector: per pair sliding five minute window with deque and running sum. observe adds tick, evicts old, average equals sum over count, flags when absolute deviation from average is at least ten percent. First ticks cold start not flagged against themselves. Multi pair isolation. Amortized O of one per tick, space O of window occupancy. Tests use fake timestamps for jump, boundary, eviction, isolation. Follow ups: min count, durable stream job, decimal rates.'))

    d.append(("interviewer",
        'Production tomorrow?'))

    d.append(("candidate",
        'I would run this as a stream processor with event time versus processing time clarified, watermarking for late data, and metrics on flag rate per pair so noisy pairs get tuned thresholds.'))

    d.append(("interviewer",
        'Why inclusive current tick can hide a jump relative to recent history?'))

    d.append(("candidate",
        'If the window is short and the jump is large, including the current point pulls the average toward the spike and can reduce the percentage. Previous only average is more sensitive. I document the choice. For a take home I would ask which definition risk wants. Both are implementable with the same deque by computing average before append or after.'))

    d.append(("interviewer",
        'Show previous only variant math in words.'))

    d.append(("candidate",
        'Evict using current timestamp first against existing deque, if count zero no baseline return false or true per policy, else average equals sum over count, compare current rate to that average, then append current and add to sum. Order is evict, compare, append. Inclusive was append, evict, compare.'))

    d.append(("interviewer",
        'Multi pair hand walk. Pair U S D E U R steady, pair U S D J P Y jumps.'))

    d.append(("candidate",
        'Ticks alternate pairs. Each pair state is isolated so a jump on Y en does not flag E U R. I test by feeding a calm E U R series and a spiked J P Y series and asserting flags only on the spiked pair indices.'))

    d.append(("interviewer",
        'How do you unit test eviction without flaky sleep?'))

    d.append(("candidate",
        'All timestamps are numbers I choose. Tick at zero, tick at ten, tick at four hundred. After four hundred, zero must be gone if window is three hundred. I assert on an internal count method or on behavior that only matches post eviction averages.'))

    d.append(("interviewer",
        'Late data and out of order in real FX feeds.'))

    d.append(("candidate",
        'Event time systems use watermarks and may buffer. This interview store raises or rejects reverse timestamps per pair. I mention that production stream jobs differ, so we do not pretend the in memory class is a full Flink job.'))

    d.append(("interviewer",
        'Threshold configuration per pair?'))

    d.append(("candidate",
        'Map from pair to threshold with default. observe looks up threshold. Thin extension. Emerging market pairs may need wider bands.'))

    d.append(("interviewer",
        'Numerical example for exactly ten percent boundary.'))

    d.append(("candidate",
        'Window with average one point zero, current one point one. Absolute difference over average equals zero point one, greater or equal threshold flags true. Current one point zero nine nine may be false depending on float. I use greater or equal and a simple fraction in tests to avoid ugly floats when possible.'))

    d.append(("interviewer",
        'If rates are mid prices that flicker, how do you avoid alert fatigue?'))

    d.append(("candidate",
        'Min tick count, hysteresis, or require consecutive anomalous ticks. Follow ups. Core interview remains one tick versus window average.'))

    d.append(("interviewer",
        'Data structure choice: why not a time sorted list binary search each time?'))

    d.append(("candidate",
        'Works but heavier. Deque fits because we only evict from the left under non decreasing timestamps. If random time inserts were allowed, I would need an ordered multiset and careful sum maintenance, much harder live.'))

    d.append(("interviewer",
        'Closing production metrics.'))

    d.append(("candidate",
        'Flags per pair per hour, window size occupancy, observe latency, skip counts for out of order. Those tell you if the detector is useful or noisy.'))

    d.append(("interviewer",
        'Simulate coding phase. Narrate imports and class skeleton.'))

    d.append(("candidate",
        'I import deque from collections. I define class F X Anomaly Detector. Constructor takes window seconds default three hundred, threshold default zero point one. I validate both positive. I store them. I create dict pair states empty. Optionally a small dataclass Pair State with deque, sum, last timestamp.'))

    d.append(("interviewer",
        'Continue with observe body order.'))

    d.append(("candidate",
        'Validate rate positive. Get or create state for pair. If last timestamp is not none and timestamp less than last raise Value Error out of order. Append tuple timestamp rate, sum plus equals rate, last equals timestamp. While deque and deque zero zero less than timestamp minus window: pop left and subtract rate from sum. Average equals sum divided by length. Return absolute rate minus average divided by average greater or equal threshold.'))

    d.append(("interviewer",
        'Tests you write with numeric literals.'))

    d.append(("candidate",
        'Detector window three hundred threshold zero point one. observe pair A at zero rate one false. at ten rate one false. at twenty rate one point two true roughly. Second pair B only steady ones all false while A may flag. Then at four hundred rate one on A after sparse history: eviction path. Exactly one point one on average one boundary true.'))

    d.append(("interviewer",
        'Debug: flags every first tick. Cause?'))

    d.append(("candidate",
        'Maybe comparing to zero average from empty window before append. Fix order: append first so count at least one, average equals self, deviation zero. Or if previous only variant with empty baseline I must define false.'))

    d.append(("interviewer",
        'Debug: multi pair cross talk. Cause?'))

    d.append(("candidate",
        'Accidentally used a single global deque. Fix map keyed by pair. Test isolation.'))

    d.append(("interviewer",
        'How would you explain five minute average to a risk analyst in plain language?'))

    d.append(("candidate",
        'For each currency pair we keep the recent mid prices from the last five minutes and check whether the newest price is at least ten percent away from that short average. It is an early noise alarm, not a trading signal by itself.'))

    d.append(("interviewer",
        'Would you use this alone for production trading halts?'))

    d.append(("candidate",
        'No. It is a coding exercise style detector. Production risk needs venue health, bid ask integrity, and human policy. I keep scope honest in the interview.'))

    d.append(("interviewer",
        'Streaming system design one level up without leaving coding land too far.'))

    d.append(("candidate",
        'This class is the per process pure function of ticks to booleans. Upstream parsers feed ticks. Downstream alert sinks consume trues. Scaling means partitioning by pair. I can say that in four sentences then return to the deque.'))

    d.append(("interviewer",
        'Final minutes priority?'))

    d.append(("candidate",
        'Eviction correctness test, isolation test, boundary ten percent test, spoken amortized O of one. No Flink rewrite.'))

    d.append(("narrator",
        'Speed recap. FX ticks per pair. Five minute window. Deque plus running sum. Ten percent versus average. Evict old. Isolate pairs. Amortized O of one. Fake clock tests. Code AI off after listen.'))

    return d
