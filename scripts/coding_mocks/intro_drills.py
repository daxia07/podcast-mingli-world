"""90-second intro variants for Stage 1."""


def build():
    d = []

    d.append(("narrator",
        'Intro drills. Official budget about two minutes. Aim sixty to ninety seconds. Substance, not flattery.'))

    d.append(("interviewer",
        'Please introduce yourself briefly.'))

    d.append(("candidate",
        'I am Mingxia. I build AI tooling and automation in fintech contexts, including multi agent workflows and production safety checks. I care about clean interfaces, tests, and systems that stay correct under retries. I am excited about Airwallex because you combine global financial infrastructure with an AI native engineering culture. Happy to jump into the coding problem.'))

    d.append(("narrator",
        'Variant two, slightly more systems.'))

    d.append(("interviewer",
        'Tell me about yourself.'))

    d.append(("candidate",
        'I am a software engineer focused on AI platforms and backend automation. Recently I have worked on orchestrating agents, hardening pipelines, and making sure tools fail safely. I like problems where algorithms meet production constraints like rate limits and idempotency. Ready for the exercise when you are.'))

    d.append(("narrator",
        'Variant three, shorter.'))

    d.append(("interviewer",
        'Quick intro.'))

    d.append(("candidate",
        'Mingxia, AI tooling and fintech engineering. I ship practical systems with clear tests and operational judgment. Excited to work a problem with you.'))

    d.append(("narrator",
        "Anti patterns: ten minute life story, resume monologue, flattering the interviewer's Twitter, apologizing for nerves for thirty seconds. Stop talking and let them give the problem."))

    return d
