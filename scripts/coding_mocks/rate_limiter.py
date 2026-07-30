"""Mock coding interview (~20 min): Rate limiter — problem segment only."""


def build():
    d = []

    d.append(("narrator",
        'This is a coding mock interview focused only on the problem block. Expect about twenty minutes of interviewer and candidate dialogue. There is no system design detour and no AI tools in this segment. Listen with your ears. On a second play, pause after each interviewer question and answer yourself before the candidate speaks. On a third play, shadow the candidate line by line to build muscle memory.'))

    d.append(("interviewer",
        'Hi, thanks for coming in. We are going to spend this block on a single coding problem, roughly the same way the first half of our coding interview works. You may use Python. Please do not use AI code completion or chat tools during this segment. I will state a real world scenario. I want you to clarify requirements, explain your approach, walk an example, describe pseudocode in full words, and cover corner cases and complexity. You do not need to pretend to type every character in this audio version, but speak as if you are about to implement. Ready?'))

    d.append(("candidate",
        'Yes. Please go ahead with the problem.'))

    d.append(("interviewer",
        'Here is the problem. We run an AI agent platform where many customers invoke large language model endpoints through agents. Each caller has a client id string. I need a rate limiter that protects shared model capacity. The core API is simple: allow client id returns true if this call may proceed, and false if it should be rejected. Functional requirements. First, support burst traffic so a client can send a short spike of requests above the long run average. Second, support a sustained average rate so a client cannot consume unbounded budget over time. Third, keep state in memory for this exercise. Fourth, keep the design small enough that a correct solution fits in a short coding session. Non functional expectations. I care about clear structure, explicit edge cases, and honest complexity. I also care that you do not rush into typing before the contract is clear. What questions do you have for me?'))

    d.append(("candidate",
        'I will restate the problem in my own words first. I need a per client admission controller for model API calls. The main method is allow of client id returning a boolean. It must allow short bursts but enforce a long run average rate. In memory state is acceptable. Now clarifying questions that actually change the design. Is the limit scoped per client id rather than one global bucket shared by everyone? Is a boolean sufficient, or do you also need a retry after duration in this first version? Should capacity and refill rate be constructor parameters? Is refill rate in tokens per second? For concurrency, is single threaded logic enough for this segment, as long as I can explain how to lock later? For time, may I use a monotonic clock so wall clock jumps do not break refill math? Finally, is one token always equal to one API call, or can costs differ by call type?'))

    d.append(("interviewer",
        'Excellent questions. Yes, per client id. Boolean only is enough for the first cut. Constructor takes capacity and refill rate in tokens per second. Single threaded is fine for implementation now. Monotonic clock is preferred. Assume cost one per call unless we extend later. You may choose token bucket or sliding window. Tell me which and why before algorithms detail.'))

    d.append(("candidate",
        'I will use a token bucket per client. Capacity C is the maximum burst. Refill rate R restores tokens continuously as time passes, measured in tokens per second. Each allowed call spends one token. Why not a fixed window counter that stores timestamps? Fixed windows are easy to implement but can almost double burst near window boundaries, and under high traffic the timestamp lists cost memory and scan time. Why not a pure sliding log? More accurate in some senses, but heavier than we need for an interview thin slice. Token bucket matches how many API gateways talk about burst plus sustained rate, and each allow can be constant time with a hash map from client to state. One sentence of product framing for an ML infrastructure audience: this is how I would protect model serving capacity per tenant when agents burst tool calls. I will still present a naive approach first, then the improved structure, because that is good interview process.'))

    d.append(("interviewer",
        'Walk me through naive and improved carefully. Still no code.'))

    d.append(("candidate",
        'Naive approach. Maintain a map from client id to a list of timestamps of recent successful allows. On allow, drop timestamps older than one second, count what remains, if under the limit append the current time and return true, otherwise return false. This is understandable and roughly enforces a per second cap. Its weaknesses are boundary bursts, O of events in the window per call, and memory growth with traffic. Improved approach with token bucket. Map client id to a small state object containing tokens remaining as a float, and last refill timestamp. On allow, compute elapsed equals now minus last refill using monotonic time. Clamp elapsed to be at least zero defensively. Add elapsed times refill rate to tokens, then cap tokens at capacity. Set last refill to now. If tokens is at least one, subtract one, persist state, return true. Otherwise persist the refilled tokens, return false. A brand new client starts with tokens equal to capacity so they receive their burst immediately. Expected time per allow is O of one with a hash map. Space is O of number of distinct clients observed.'))

    d.append(("interviewer",
        'What specifically breaks if you refill but forget to cap?'))

    d.append(("candidate",
        'A client that stays idle for a long time could accumulate a huge token balance. Then they could dump a burst much larger than capacity. That violates the burst contract even though the long run average math looked fine. Capping after refill is load bearing, not cosmetic.'))

    d.append(("interviewer",
        'Hand walk capacity two, refill rate one token per second. Narrate every step.'))

    d.append(("candidate",
        'Client A is new, so tokens start at two, last refill is now. First allow: tokens at least one, spend, tokens become one, return true. Second allow immediately: spend, tokens become zero, return true. Third allow immediately: tokens less than one after refill of roughly zero elapsed, return false. Advance time by one second. On the next allow, elapsed is about one, tokens becomes min of two and zero plus one, so one, then spend to zero, return true. Client B never appears in A state. When B first shows up, B gets its own full capacity two. Isolation is part of correctness, not an afterthought.'))

    d.append(("interviewer",
        'Describe classes, fields, and method signatures you will implement.'))

    d.append(("candidate",
        'Class Token Bucket Limiter. Constructor takes capacity, refill rate, and optionally a now function for tests. I validate capacity and rate are not negative. I store capacity, refill rate, the now function defaulting to time monotonic, and an empty dict mapping client id strings to bucket state. Bucket state has tokens float and last refill float seconds. Public method allow client id returns bool. I may later add try allow returning allowed and retry after, but boolean allow is enough for the stated API.'))

    d.append(("interviewer",
        'Give full word pseudocode for allow. Speak as if I cannot see a screen.'))

    d.append(("candidate",
        'Method allow client id. If client id is not in the map, create a bucket state with tokens equal to capacity and last refill equal to now function, then store it. State equals the map entry for client id. Now equals call now function. Elapsed equals max of zero and now minus state last refill. State tokens equals minimum of capacity and state tokens plus elapsed times refill rate. State last refill equals now. If state tokens is greater than or equal to one, then state tokens equals state tokens minus one, write state back, return true. Else write state back, return false. Load bearing order: get or create, refill, cap, then spend. I use full names: capacity, refill rate, client id, last refill, not single letter soup.'))

    d.append(("interviewer",
        'How do tests avoid real sleeps if refill depends on time?'))

    d.append(("candidate",
        'I inject a clock. In tests I pass a fake now function that returns values I control, like a list of timestamps I pop, or a mutable variable I advance. Production constructor omits it and uses monotonic time. That keeps unit tests fast and deterministic.'))

    d.append(("interviewer",
        'Walk corner cases one by one and say what the code should do.'))

    d.append(("candidate",
        'Unknown client: first allow creates a full bucket, so burst is available. Empty string client id: I will treat it as a normal key unless product policy rejects empty identifiers; I will state that assumption. Capacity zero: every allow returns false. Refill rate zero: only the initial burst works, then permanent false until config changes. Very large idle elapsed: cap prevents infinite tokens. Rapid fire exactly capacity successes then one failure. Two clients interleaved: no shared tokens. Negative capacity or rate in constructor: raise invalid argument at construction time.'))

    d.append(("interviewer",
        'Name the unit tests you would write before claiming done.'))

    d.append(("candidate",
        'test burst of two then reject on third. test refill after one second of fake time restores a token. test clients are isolated. test capacity zero. test rate zero only initial burst. test long idle does not exceed capacity. test constructor rejects negative inputs. Those tests pin the contract without flaky sleeps.'))

    d.append(("interviewer",
        'If I ask for thread safety before we finish, what is the smallest correct change?'))

    d.append(("candidate",
        'A single mutex around the body of allow is the smallest correct change. It serializes all clients, which may be fine initially. A better step is a lock per client state, with double checked creation so two threads creating the same client do not corrupt the map. I would not jump to a distributed Redis counter unless we change the problem to multi process.'))

    d.append(("interviewer",
        'Why must allow stay non blocking?'))

    d.append(("candidate",
        'Allow sits on a request path. Sleeping or spinning until a token exists couples worker threads to wait time and makes overload worse. Prefer returning false quickly. If product needs guidance, expose retry after seconds in a richer return type without blocking.'))

    d.append(("interviewer",
        'Derive retry after math in words.'))

    d.append(("candidate",
        'After refill and cap, if tokens is at least one, retry after is zero and we may spend. If tokens is less than one, need equals one minus tokens. When refill rate is greater than zero, retry after seconds equals need divided by rate. When rate is zero and tokens is insufficient, retry after is unbounded; I would return none or a documented sentinel.'))

    d.append(("interviewer",
        'I extend the problem: health checks should not consume tokens, but model calls cost one. How do you adapt without a rewrite?'))

    d.append(("candidate",
        'Add an optional cost parameter defaulting to one, or a separate method allow with cost. Spending checks tokens greater or equal cost, then subtracts cost. Health checks pass cost zero, or skip the limiter. Refill and cap stay identical.'))

    d.append(("interviewer",
        'Complexity summary?'))

    d.append(("candidate",
        'Time per allow is O of one expected for hash map operations plus constant arithmetic. Space is O of number of distinct clients. If clients accumulate forever, a later improvement is idle eviction with time to live. I would not implement eviction unless you ask.'))

    d.append(("interviewer",
        'You have a working happy path and a few minutes left on the problem block. What do you do?'))

    d.append(("candidate",
        'I do not start a distributed redesign. I add the highest value tests with the fake clock, restate complexity out loud, and write a short class docstring describing capacity, rate, and monotonic time. Working readable code beats unfinished cleverness.'))

    d.append(("interviewer",
        'Good. In a live session I would now watch you implement the class in the editor. For this audio episode, your homework is to implement Token Bucket Limiter from a blank file without AI, using the hand walk and the test list we spoke.'))

    d.append(("candidate",
        'Understood. I would scaffold the class with injectable clock first, write failing tests for burst and isolation, then implement allow until tests pass.'))

    d.append(("interviewer",
        'Let us simulate the implementation phase. Narrate the code you would type in order, as if I am watching your editor. Full words, no silent typing.'))

    d.append(("candidate",
        'I start a new file limiter.py. I import time for monotonic. I define class Token Bucket Limiter. In the constructor I accept capacity, refill rate, and optional now function defaulting to time monotonic. I validate capacity and rate are greater or equal zero, else raise Value Error. I store capacity, refill rate, now function, and an empty dict named buckets.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I define a simple Bucket State using a small class or a typed namespace with tokens and last refill. I prefer an explicit class for readability in interviews. Tokens is a float. Last refill is a float seconds value from the clock.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I implement allow client id. First I check if client id is missing from buckets. If missing I create Bucket State with tokens equal capacity and last refill equal self now function call, then assign into buckets. Next I read state equals buckets client id.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I compute now equals self now. Elapsed equals max of zero and now minus state last refill. I set state tokens equals min of capacity and state tokens plus elapsed times refill rate. I set state last refill equals now.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I branch. If state tokens is at least one, I subtract one from state tokens, write buckets client id equals state, return true. Else I write state back and return false. I keep names long so the interviewer can follow on screen share.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'I add a module level note in a docstring: single threaded, monotonic clock, cost one per call. I am not adding Redis. I then write tests in test limiter.py using a fake clock list that returns predetermined times so I never sleep.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'First test constructs limiter capacity two rate one with fake clock. I call allow A true, allow A true, allow A false. I advance fake time by one second. I call allow A true. Second test uses clients A and B to prove isolation. Third test capacity zero. Fourth test rate zero after burst.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'If a test fails because I forgot to write state back, I fix by always assigning buckets client id equals state before return. If refill overshoots, I recheck the min cap line. I re-run until green.'))

    d.append(("interviewer",
        'Continue. What do you type next, and why?'))

    d.append(("candidate",
        'Finally I speak complexity again while looking at the code: each allow is hash map plus arithmetic, expected constant time, space linear in clients. I stop adding features.'))

    d.append(("interviewer",
        'Good. Pause. Any compile time or test failure you anticipate?'))

    d.append(("interviewer",
        'Before we close, summarize the whole solution in about one minute, as you would at the end of a real problem block.'))

    d.append(("candidate",
        'I implemented a per client token bucket rate limiter for model API admission. Constructor takes capacity as burst size, refill rate in tokens per second, and an optional clock for tests. Allow refills tokens using monotonic elapsed time, caps at capacity, then spends one token if available. New clients start full. Tests use a fake clock covering burst, refill, isolation, capacity zero, and rate zero. Single threaded now, locks later if needed. Allow stays non blocking. Time O of one expected, space O of clients. Follow ups include retry after, per call cost, and distributed stores.'))

    d.append(("interviewer",
        'What would you do differently if this were production tomorrow?'))

    d.append(("candidate",
        'I would add metrics for allow and reject counts per client, structured logs without leaking secrets, configuration hot reload, and a distributed limiter only if we run many gateway instances. I would keep the same bucket math so local tests still match production semantics as much as possible.'))

    d.append(("interviewer",
        'Any open questions you would ask product before shipping?'))

    d.append(("candidate",
        'Whether reject should be hard fail or queue, whether internal services share client ids, and whether we need different limits per model tier. Those change API shape more than the core bucket.'))

    d.append(("narrator",
        'Speed recap for daily muscle memory. Problem: per client allow for agent model API with burst and sustained rate. Clarify: boolean, in memory, single thread, monotonic clock, cost one. Naive: timestamp lists in a fixed window. Better: token bucket map, refill, cap, spend. Fake clock for tests. Corners: new client full, capacity zero, rate zero, isolation, long idle cap. Optional: retry after, per call cost, per client locks. Non blocking allow. Complexity O of one time, O of clients space. Replay until you can perform the candidate role without this recording, then code for thirty minutes with AI off.'))

    return d
