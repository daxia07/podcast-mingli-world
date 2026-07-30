"""Wrong answer vs fix lines for Airwallex coding."""


def build():
    d = []

    d.append(("narrator",
        'Wrong answers clinic. Hear the failure, then the fix line. Replay until the fix is automatic.'))

    d.append(("interviewer",
        'Candidate said: I will just start coding the optimal solution now.'))

    d.append(("candidate",
        'Better: I will restate, ask two clarifiers, state a naive approach, then improve.'))

    d.append(("interviewer",
        'Candidate said: I opened Copilot because the first thirty minutes are hard.'))

    d.append(("candidate",
        'Better: AI stays off until the deep dive segment. Violation risk is extreme.'))

    d.append(("interviewer",
        'Candidate said: BFS should find the best currency conversion.'))

    d.append(("candidate",
        'Better: BFS optimizes hops. Best rate needs product maximisation, usually negative log and Dijkstra.'))

    d.append(("interviewer",
        'Candidate said: I will sleep inside allow until a token exists.'))

    d.append(("candidate",
        'Better: Allow must be non blocking. Return false or retry after guidance instead.'))

    d.append(("interviewer",
        'Candidate said: Silent coding for five minutes is fine if I am fast.'))

    d.append(("candidate",
        'Better: Narrate loop purpose. Silence loses process signal.'))

    d.append(("interviewer",
        'Candidate said: I will mutate the refunded amount then run the rules.'))

    d.append(("candidate",
        'Better: Run all rules first. Mutate only on full pass.'))

    d.append(("interviewer",
        'Candidate said: Float dollars are ok for refunds.'))

    d.append(("candidate",
        'Better: Use integer minor units for money.'))

    d.append(("interviewer",
        'Candidate said: If stuck I should apologize until time ends.'))

    d.append(("candidate",
        'Better: Step back, two options, constraint decides, ask if needed.'))

    d.append(("interviewer",
        'Candidate said: First AI prompt: rewrite my entire file optimally.'))

    d.append(("candidate",
        'Better: Directed prompt for tests or one edge. Verify every diff.'))

    d.append(("interviewer",
        'Candidate said: I need ten minutes of background chat.'))

    d.append(("candidate",
        'Better: Sixty to ninety seconds intro, then the problem.'))

    d.append(("narrator",
        'End clinic. Prefer the better line every time.'))

    return d
