
"""Full ~60 min dual-mode mock: intro + rate limiter problem + AI deep dive."""

from .rate_limiter import build as build_problem
from .ai_deep_dive_part2 import build as build_deep


def build():
    d = []
    d.append(("narrator",
        "Full coding interview simulation. About one hour of content. "
        "Segment one short intro. Segment two problem without AI. Segment three deep dive with AI allowed. "
        "Two voices. Listen as a dress rehearsal. "
        "You may pause between segments to actually code."))

    d.append(("interviewer",
        "Welcome. This is a sixty minute coding interview. "
        "Two minutes for a brief intro, then a coding problem without AI tools, then a technical deep dive where AI tools are allowed. "
        "Please start with a short introduction."))

    d.append(("candidate",
        "I am Mingxia. I build AI tooling and automation around reliable backend systems in fintech contexts. "
        "I focus on clear interfaces, tests, and safe behavior under retries and load. "
        "I am excited about Airwallex combining global payments infrastructure with AI native engineering. "
        "Happy to take the problem."))

    d.append(("interviewer", "Great. AI tools are off for the next segment. Here is the problem."))

    # problem body without its outer narrator bookends if present
    problem = build_problem()
    # drop first narrator and last narrator from problem for cleaner hour
    if problem and problem[0][0] == "narrator":
        problem = problem[1:]
    if problem and problem[-1][0] == "narrator":
        problem = problem[:-1]
    # skip problem's own hi thanks joining if duplicate - keep all for substance
    d.extend(problem)

    d.append(("narrator",
        "Hard switch. In a real interview the interviewer now opens the deep dive. "
        "AI tools become allowed. Do not open them early."))

    d.append(("interviewer",
        "Time on the pure coding segment is up. "
        "We now enter the technical deep dive. AI tools are allowed. "
        "Open your assistant if you want and we will improve what you have."))

    deep = build_deep()
    if deep and deep[0][0] == "narrator":
        deep = deep[1:]
    if deep and deep[-1][0] == "narrator":
        deep = deep[:-1]
    # skip deep's first interviewer if redundant - keep content
    d.extend(deep)

    d.append(("interviewer",
        "That concludes the interview block. Do you have a quick question for me if time remains?"))

    d.append(("candidate",
        "One short question: how does the team usually review AI assisted changes in production pull requests?"))

    d.append(("interviewer",
        "We expect the same quality bar as human code: tests, readability, and ownership. "
        "Thanks for your time."))

    d.append(("candidate", "Thank you."))

    d.append(("narrator",
        "Hour complete. "
        "Practice mode: after segment two pause and really code for thirty minutes AI off, then resume deep dive and practice Claude Code prompts. "
        "Replay weekly until the switch is automatic."))

    return d
