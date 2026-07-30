"""Short drills: stuck recovery lines (two-voice)."""


def build():
    d = []

    d.append(("narrator",
        'Stuck recovery pack. Short two voice drills. When you freeze, you need lines not panic. Replay daily.'))

    d.append(("interviewer",
        'You have been quiet for a while. What are you thinking?'))

    d.append(("candidate",
        'Let me take a step back and think systematically. I am between two approaches. A is nested loops, O of n squared. B uses a hash map for constant lookups. Given n can be large, I should take B. If I am missing a constraint, tell me.'))

    d.append(("interviewer",
        'Good. Continue with B.'))

    d.append(("narrator",
        'Recovery one: name two options and the constraint that picks. Never only sorry.'))

    d.append(("interviewer",
        'Your tests fail on the empty case.'))

    d.append(("candidate",
        'I see a bug on the empty input. I will return early with the documented empty result before the main loop. Fixing that now, then re-running the same example.'))

    d.append(("narrator",
        'Recovery two: name the bug, the fix, then re-verify. Silence is worse than a small bug.'))

    d.append(("interviewer",
        'We have eight minutes left and only a slow solution.'))

    d.append(("candidate",
        'I will ship the correct O of n squared version that works, state its complexity, and spend remaining minutes on one clear optimise if it is safe. Working solution first beats unfinished optimal.'))

    d.append(("narrator",
        'Recovery three: prioritize working code under time pressure.'))

    d.append(("interviewer",
        'That approach will not handle duplicates correctly.'))

    d.append(("candidate",
        'Thanks. The invariant broke on duplicates. I will adjust the map update order: lookup complement before insert so I never pair an element with itself. Hand walk with three three target six, then recode that line.'))

    d.append(("narrator",
        'Recovery four: accept feedback, restate invariant, hand walk, fix.'))

    d.append(("interviewer",
        'You look stuck on which data structure to pick.'))

    d.append(("candidate",
        'The operation I need is have I seen this key before with a value. That is map membership and payload, not a list scan. I will commit to a hash map and implement the simple version first.'))

    d.append(("narrator",
        'Recovery five: name the operation, pick the structure, commit.'))

    d.append(("narrator",
        'Card for every freeze. Step back. Two options. Constraint decides. Hand walk. Code. If time dies, correct first.'))

    return d
