"""Mock: Part 2 AI deep dive pilot (two-voice)."""


def build():
    d = []

    d.append(("narrator",
        'Coding mock, part two only. Technical deep dive with AI tools allowed. About twenty minutes. Assume part one already produced a working token bucket rate limiter without AI. Interviewer reviews. Candidate uses Claude Code with directed prompts and verification. Loop this until the pilot script is automatic.'))

    d.append(("interviewer",
        'We are now in the technical deep dive. AI assisted tools are allowed. You may open Claude Code or similar. We will improve the solution you already wrote. Please summarize what you have and what you want to improve first.'))

    d.append(("candidate",
        'I have a single threaded token bucket limiter. Constructor takes capacity, refill rate, and an injectable clock. Allow refills, caps, then spends one token per client. Happy path works for burst and isolation. Gaps I want to close first: stronger unit tests, capacity zero and rate zero edges, and a clear retry after helper without rewriting the core. I am enabling AI only now because this segment allows it.'))

    d.append(("interviewer",
        'Show me how you use the tool. Narrate the first prompt before you accept anything.'))

    d.append(("candidate",
        'I open Claude Code on the same project. First prompt: add unit tests for empty client handling as documented, capacity zero always false, rate zero only initial burst, and two client isolation. Do not change production logic unless a test forces a fix. Show the test file first if possible.'))

    d.append(("interviewer",
        'The model returns a large diff. What do you do?'))

    d.append(("candidate",
        'I read the diff out loud enough that you can hear I am not blind accepting. I check that tests use the fake clock, not real sleep. I run the test suite. If green, I keep the tests. If a test assumes sorted client ids or invents retry after in allow, I reject that part.'))

    d.append(("interviewer",
        'Give me an example of rejecting a bad suggestion.'))

    d.append(("candidate",
        'Suppose the model rewrites allow to sleep until a token is free. I reject that. Reason: allow must stay non blocking on a request path. I say that to you, not only to the model, then prompt: keep allow non blocking, add a separate method that only computes retry after seconds.'))

    d.append(("interviewer",
        'Walk a good second and third prompt.'))

    d.append(("candidate",
        'Second prompt: list edge cases I likely missed for a multi tenant agent API rate limiter. Do not code yet. I pick two: long idle cap, and cost parameter for expensive model calls. Third prompt: implement try allow returning allowed bool and retry after seconds using existing refill math. Do not block. Add tests with fake clock. Then I run tests again and hand walk capacity two failure retry after about one second when rate is one.'))

    d.append(("interviewer",
        'How do you check complexity claims with AI?'))

    d.append(("candidate",
        'Prompt: is my claim O of one time and O of number of clients space accurate? Point to the lines. If the model claims linear scan somewhere, I look at the code myself. If I still have a dict keyed by client and constant arithmetic, I keep O of one expected time. I do not let the model invent Big O without line references.'))

    d.append(("interviewer",
        'Thread safety. Use AI carefully.'))

    d.append(("candidate",
        'I ask: suggest the smallest correct thread safety change for allow, with trade offs between one global lock and per client locks. Do not apply yet. I explain the trade off to you: global lock is simple, per client lock scales better. Then I choose per client lock for discussion quality, or global lock if time is short. I apply only after I can explain every line.'))

    d.append(("interviewer",
        'What do you never do in this segment?'))

    d.append(("candidate",
        'I never paste rewrite the whole solution as the first prompt. I never accept code I cannot explain. I never hide that a test failed. I never open AI before this segment in the real interview.'))

    d.append(("interviewer",
        'How do you use AI day to day, in one short answer?'))

    d.append(("candidate",
        'I use agents for tests, exploration, and refactors. I keep design ownership. I run verification. AI generated code meets the same bar as mine.'))

    d.append(("interviewer",
        'We have five minutes. Prioritize.'))

    d.append(("candidate",
        'I finalize tests and retry after. I skip distributed Redis unless you insist. I restate remaining risks: multi instance limits need a shared store, metrics not implemented, eviction of idle clients not implemented.'))

    d.append(("interviewer",
        'Good deep dive.'))

    d.append(("candidate",
        'Thank you.'))

    d.append(("interviewer",
        'Show a fourth prompt that only improves names without behavior change.'))

    d.append(("candidate",
        'Prompt: rename variables for clarity only, keep behavior identical, no new dependencies. Then I read the diff and run tests to prove no behavior change.'))

    d.append(("interviewer",
        'The model adds an external package for redis. Response?'))

    d.append(("candidate",
        'I reject it for this segment. We agreed in memory. I say: stay with the in memory map, no new dependencies, restate the multi instance follow up verbally instead.'))

    d.append(("interviewer",
        'How do you keep me in the loop while the tool runs?'))

    d.append(("candidate",
        'I narrate the goal before the prompt, narrate what I see in the diff, narrate the test command and result, then state my decision. You should never wonder whether I understand the change.'))

    d.append(("interviewer",
        'Ask yourself an adversarial question the model might get wrong.'))

    d.append(("candidate",
        'Does refill use wall clock? I check the code path still calls the injectable monotonic now. If the model switched to datetime now, I revert that line.'))

    d.append(("interviewer",
        'Wrap up metrics you would add with AI help.'))

    d.append(("candidate",
        'I prompt for a thin counters dict or simple class fields: allows, rejects, optional per client rejects. I avoid a full metrics platform. Tests assert reject counter increments on capacity zero.'))

    d.append(("interviewer",
        'Final recap of the deep dive process you want me to remember.'))

    d.append(("candidate",
        'Summarize gaps, directed prompts, read, run, decide, reject bad ideas out loud, leave production follow ups explicit, keep ownership.'))

    d.append(("interviewer",
        'Walk me through a complete five prompt plan as a checklist before you touch the tool.'))

    d.append(("candidate",
        'One: generate tests for capacity zero, rate zero, isolation, burst, with fake clock only. Two: list edges without code. Three: implement try allow retry after non blocking. Four: complexity audit pointing at lines. Five: optional thin metrics counters. After each, run tests and decide.'))

    d.append(("interviewer",
        'Demonstrate prompt one wording exactly.'))

    d.append(("candidate",
        'Add pytest tests for TokenBucketLimiter using an injectable clock. Cover burst of two then reject, refill after one second, two clients isolation, capacity zero, rate zero after burst. Do not use time.sleep. Do not modify production code unless a test fails because of a real bug.'))

    d.append(("interviewer",
        'Demonstrate rejecting a model change that alters the public API without asking.'))

    d.append(("candidate",
        'If it renames allow to check quota without a deprecation path, I reject and say keep allow signature stable, add new methods alongside.'))

    d.append(("interviewer",
        'How do you pair with me while multi tasking on the tool?'))

    d.append(("candidate",
        'I keep a spoken cadence: goal, prompt, wait, summarize diff in one sentence, test result, decision. If a run is long I still narrate what I am waiting for.'))

    d.append(("interviewer",
        'Security angle: the model wants to log full client ids and prompts at info level.'))

    d.append(("candidate",
        'I reject verbose PII style logging. I allow aggregated counters and hashed or truncated ids if needed. Finance and AI platforms are sensitive to log leakage.'))

    d.append(("interviewer",
        'Performance angle: the model suggests pre creating buckets for all possible clients.'))

    d.append(("candidate",
        'I reject precreation of unbounded client spaces. Lazy creation on first allow is correct. Eviction can come later.'))

    d.append(("interviewer",
        'Now pretend tests failed. Show recovery with AI.'))

    d.append(("candidate",
        'I read the failure. I prompt: failing test name and assertion, here is the code, propose minimal fix, do not refactor unrelated. I apply only if the fix matches the bucket invariant. Then re-run full file tests.'))

    d.append(("interviewer",
        'Give your closing deep dive speech.'))

    d.append(("candidate",
        'We strengthened tests, kept allow non blocking, added retry after without rewriting admission, verified complexity, discussed locks and multi instance as follow ups, and used AI as a junior pair under my review. I own every accepted line.'))

    d.append(("narrator",
        'Speed recap for part two. Summarize gaps. Directed prompts only. Read diff, run tests, accept or reject out loud. Reject blocking rewrites. Verify complexity on real lines. You stay lead. Loop until the prompt templates are boring.'))

    return d
