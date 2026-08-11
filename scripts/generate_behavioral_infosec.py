#!/usr/bin/env python3
"""generate_behavioral_infosec.py — Generate behavioral interview and info security episodes.

Creates compilation-style episodes from the content bank prompts and info_security sections.
Audio-first design: natural spoken transitions, numbered lists, pause markers, no visual formatting.
"""

# Frozen — see scripts/_legacy_guard.py. New episodes: build_episode.py
from _legacy_guard import warn_legacy
warn_legacy(__file__)


import json, os, sys
from datetime import datetime, timezone

from tts import synthesize, get_duration_str


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_BANK_PATH = os.path.join(SCRIPT_DIR, "content_bank.json")
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

BEHAVIORAL_EPISODES = [
    {
        "id": 450, "theme": "behavioral-why-leaving-weakness",
        "title": "Why Leaving + Biggest Weakness",
        "prompt_ids": ["why-leaving", "biggest-weakness"],
    },
    {
        "id": 451, "theme": "behavioral-deadline-feedback",
        "title": "Tight Deadlines + Critical Feedback",
        "prompt_ids": ["tight-deadline", "received-critical-feedback"],
    },
    {
        "id": 452, "theme": "behavioral-unpopular-difficult",
        "title": "Unpopular Decisions + Difficult People",
        "prompt_ids": ["right-decision-unpopular", "worked-with-difficult-person"],
    },
    {
        "id": 453, "theme": "behavioral-ambiguity-standards",
        "title": "Navigating Ambiguity + Driving Standards",
        "prompt_ids": ["dealt-with-ambiguity", "promoted-adopted-standard"],
    },
    {
        "id": 454, "theme": "behavioral-quality-incident",
        "title": "Quality vs Speed + Production Incidents",
        "prompt_ids": ["balanced-quality-speed", "handled-production-incident"],
    },
]

INFOSEC_EPISODES = [
    {
        "id": 460, "theme": "infosec-owasp-auth",
        "title": "OWASP Top 10 + Authentication Patterns",
        "concept_ids": ["owasp-top-10", "authentication-authorization"],
        "prompt_ids": ["infosec-security-vs-delivery"],
    },
    {
        "id": 461, "theme": "infosec-encryption-threatmodel",
        "title": "Encryption + Threat Modeling",
        "concept_ids": ["encryption-at-rest-transit", "threat-modeling"],
        "prompt_ids": ["infosec-vulnerability-response"],
    },
    {
        "id": 462, "theme": "infosec-incident-secrets",
        "title": "Incident Response + Secrets Management",
        "concept_ids": ["incident-response", "secret-management"],
        "prompt_ids": ["infosec-designed-secure-system"],
    },
    {
        "id": 463, "theme": "infosec-supplychain-compliance",
        "title": "Supply Chain Security + Compliance",
        "concept_ids": ["supply-chain-security", "compliance-regulations"],
        "prompt_ids": ["infosec-compliance-framework"],
    },
    {
        "id": 464, "theme": "infosec-zero-trust-api",
        "title": "Zero Trust Architecture + API Security",
        "concept_ids": ["zero-trust-architecture", "api-security"],
        "prompt_ids": ["infosec-zero-trust"],
    },
]

FRAMEWORK_EXPLANATIONS = {
    "STAR-LA": "Situation, Task, Action, Result, Learning. You describe the situation, what you needed to do, what you actually did, the result, and what you learned.",
    "Structure-First": "Start with your main point, then support it. Lead with the conclusion, then give the evidence.",
    "Acknowledge-Reframe": "First acknowledge the concern honestly, then reframe it as a strength or growth area.",
    "Hook-Flow-Landing": "Hook the listener with a surprising detail, flow through the story, land on the takeaway.",
    "RESHADED": "Requirements, Estimation, Storage, High-level design, API, Detailed design, Edge cases, Distinctive points. A system design interview framework.",
}


def load_content_bank():
    with open(CONTENT_BANK_PATH) as f:
        return json.load(f)


def find_prompt(content_bank, prompt_id):
    for p in content_bank.get("prompts", []):
        if p["id"] == prompt_id:
            return p
    return None


def find_concept(content_bank, concept_id):
    for c in content_bank.get("info_security", {}).get("core_concepts", []):
        if c["id"] == concept_id:
            return c
    return None


def _numbered_list(items):
    """Convert a list of items to spoken numbered format for audio clarity."""
    if len(items) <= 3:
        parts = []
        for i, item in enumerate(items, 1):
            parts.append(f"Number {i}, {item}")
        return parts
    parts = []
    for i, item in enumerate(items, 1):
        parts.append(f"{i}. {item}")
    return parts


def _framework_intro(framework_name):
    """Return a spoken introduction to a framework, or just its name if unknown."""
    explanation = FRAMEWORK_EXPLANATIONS.get(framework_name)
    if explanation:
        return f"The best framework for this answer is called {framework_name}. Here's how it works. {explanation}"
    return f"The best framework for this answer is {framework_name}."


def build_behavioral_script(episode_config, content_bank):
    today = datetime.now(timezone.utc)
    prompts = [find_prompt(content_bank, pid) for pid in episode_config["prompt_ids"]]
    prompts = [p for p in prompts if p is not None]
    total = len(BEHAVIORAL_EPISODES)
    ep_idx = next((i for i, e in enumerate(BEHAVIORAL_EPISODES) if e["id"] == episode_config["id"]), 0) + 1

    if not prompts:
        return ""

    lines = []
    lines.append(f"Welcome to Behavioral Interview Practice. {today.strftime('%B %d, %Y')}.")
    lines.append("[pause]")
    lines.append(f"This is episode {ep_idx} of {total}. Today's topic: {episode_config['title']}.")
    lines.append("[pause]")
    lines.append(f"We're covering {len(prompts)} behavioral questions. For each one, you'll get the structure, the English patterns, a sample answer, and common mistakes. Then you'll practice your own answer out loud.")
    lines.append("[pause]")

    for i, prompt in enumerate(prompts, 1):
        lines.append(f"Alright, question {i} of {len(prompts)}.")
        lines.append("[pause]")
        lines.append(prompt["text"])
        lines.append("[pause]")

        competency = prompt.get("competency", "general").replace("-", " ")
        lines.append(f"What the interviewer is really looking for here is your {competency}.")
        lines.append("")

        framework = prompt.get("framework", "STAR-LA")
        lines.append(_framework_intro(framework))
        lines.append("")

        if prompt.get("structure"):
            lines.append("Here's how to structure your answer.")
            for spoken in _numbered_list(prompt["structure"]):
                lines.append(spoken)
            lines.append("")

        if prompt.get("patterns"):
            lines.append("English patterns to use in your answer.")
            for j, pat in enumerate(prompt["patterns"], 1):
                lines.append(f"Pattern {j}. {pat}")
            lines.append("")

        if prompt.get("sample_answer"):
            lines.append("Here's a sample answer. Listen for the structure and the patterns.")
            lines.append("[pause]")
            lines.append(prompt["sample_answer"])
            lines.append("[pause]")

        if prompt.get("pitfalls"):
            lines.append("Now, common mistakes to avoid.")
            for spoken in _numbered_list(prompt["pitfalls"]):
                lines.append(spoken)
            lines.append("")

        lines.append("OK. Now it's your turn. Pause this recording and practice your own answer out loud. Use the structure and at least one of the English patterns.")
        lines.append("[long-pause]")

    lines.append("Let's do a quick review of what we covered today.")
    lines.append("[pause]")
    for i, prompt in enumerate(prompts, 1):
        lines.append(f"Question {i}. {prompt['text']}.")
        lines.append(f"Framework: {prompt.get('framework', 'STAR-LA')}. Key pattern: {prompt.get('patterns', [''])[0]}.")
        lines.append("")

    lines.append("Great work today. Remember: structure first, patterns second, practice always. See you next time.")
    lines.append("")

    return "\n".join(lines)


def build_infosec_script(episode_config, content_bank):
    today = datetime.now(timezone.utc)
    concepts = [find_concept(content_bank, cid) for cid in episode_config.get("concept_ids", [])]
    concepts = [c for c in concepts if c is not None]
    prompt = find_prompt(content_bank, episode_config["prompt_ids"][0]) if episode_config.get("prompt_ids") else None
    total = len(INFOSEC_EPISODES)
    ep_idx = next((i for i, e in enumerate(INFOSEC_EPISODES) if e["id"] == episode_config["id"]), 0) + 1

    if not concepts:
        return ""

    lines = []
    lines.append(f"Welcome to Information Security Interview Prep. {today.strftime('%B %d, %Y')}.")
    lines.append("[pause]")
    lines.append(f"This is episode {ep_idx} of {total}. Today's topic: {episode_config['title']}.")
    lines.append("[pause]")
    parts_desc = f"{len(concepts)} security concept" + ("s" if len(concepts) > 1 else "")
    if prompt:
        parts_desc += " and one behavioral question"
    lines.append(f"We're covering {parts_desc}. Let's get started.")
    lines.append("[pause]")

    for i, concept in enumerate(concepts, 1):
        lines.append(f"Alright, concept {i} of {len(concepts)}. {concept['name']}.")
        lines.append("[pause]")
        lines.append(concept.get("description", ""))
        lines.append("")

        if concept.get("key_points"):
            points = concept["key_points"]
            chunk_size = 4
            if len(points) > chunk_size:
                lines.append(f"There are {len(points)} key points. Let's go through them.")
                for chunk_start in range(0, len(points), chunk_size):
                    chunk = points[chunk_start:chunk_start + chunk_size]
                    for j, kp in enumerate(chunk, chunk_start + 1):
                        lines.append(f"Point {j}. {kp}")
                    if chunk_start + chunk_size < len(points):
                        lines.append("[pause]")
            else:
                lines.append("Let me cover the key points.")
                for j, kp in enumerate(points, 1):
                    lines.append(f"Point {j}. {kp}")
            lines.append("")

        if concept.get("trade_offs"):
            lines.append(f"Now, the trade-offs. {concept['trade_offs']}")
            lines.append("")

        if concept.get("real_examples"):
            lines.append(f"Some real-world examples. {concept['real_examples']}")
            lines.append("[pause]")

    if prompt:
        lines.append("Now let's tie this together with a behavioral question.")
        lines.append("[pause]")
        lines.append(prompt["text"])
        lines.append("[pause]")

        competency = prompt.get("competency", "general").replace("-", " ")
        framework = prompt.get("framework", "STAR-LA")
        lines.append(f"What they're looking for is your {competency}. {_framework_intro(framework)}")
        lines.append("")

        if prompt.get("sample_answer"):
            lines.append("Here's a sample answer.")
            lines.append("[pause]")
            lines.append(prompt["sample_answer"])
            lines.append("[pause]")

        if prompt.get("pitfalls"):
            lines.append("Watch out for these pitfalls.")
            for spoken in _numbered_list(prompt["pitfalls"]):
                lines.append(spoken)
            lines.append("")

        lines.append("Pause now and practice your own answer.")
        lines.append("[long-pause]")

    lines.append("Let's do a quick review.")
    lines.append("[pause]")
    for i, concept in enumerate(concepts, 1):
        desc = concept.get("description", "")
        if len(desc) > 80:
            desc = desc[:desc.rfind(" ", 0, 80)] + "."
        lines.append(f"Concept {i}. {concept['name']}. {desc}")
    if prompt:
        lines.append(f"Behavioral question. {prompt['text']}")
    lines.append("")

    lines.append("Security is everyone's responsibility. Keep learning. See you next time.")
    lines.append("")

    return "\n".join(lines)


def generate_episode(config, content_bank, episode_type):
    if episode_type == "behavioral":
        script = build_behavioral_script(config, content_bank)
    else:
        script = build_infosec_script(config, content_bank)

    if not script:
        print(f"  WARNING: Empty script for {config['theme']}")
        return None

    from tts import preprocess_text
    tts_text = preprocess_text(script)
    word_count = len(tts_text.split())
    print(f"  Script: {word_count} words, ~{word_count / 140:.0f} min estimated")

    script_path = os.path.join(DATA_DIR, f"{config['theme']}.txt")
    with open(script_path, "w") as f:
        f.write(script)

    mp3_path = os.path.join(DATA_DIR, f"{config['theme']}.mp3")
    print(f"  Generating audio...")
    synthesize(script, mp3_path, voice="legacy", rate="-15%", preprocess=True)

    size_mb = os.path.getsize(mp3_path) / (1024 * 1024)
    dur = get_duration_str(mp3_path)
    print(f"  MP3: {size_mb:.1f} MB, {dur}")

    return {
        "id": config["id"],
        "theme": config["theme"],
        "title": config["title"],
        "script_path": script_path,
        "mp3_path": mp3_path,
        "file_size_bytes": os.path.getsize(mp3_path),
        "duration": dur,
        "words": word_count,
    }


def main():
    print("=== generate_behavioral_infosec.py ===")
    os.makedirs(DATA_DIR, exist_ok=True)

    content_bank = load_content_bank()

    what = sys.argv[1] if len(sys.argv) > 1 else "all"

    results = []

    if what in ("behavioral", "all"):
        print("\n--- BEHAVIORAL INTERVIEW EPISODES ---")
        for config in BEHAVIORAL_EPISODES:
            print(f"\n  #{config['id']}: {config['title']}")
            result = generate_episode(config, content_bank, "behavioral")
            if result:
                results.append(("behavioral", result))

    if what in ("infosec", "all"):
        print("\n--- INFO SECURITY EPISODES ---")
        for config in INFOSEC_EPISODES:
            print(f"\n  #{config['id']}: {config['title']}")
            result = generate_episode(config, content_bank, "infosec")
            if result:
                results.append(("infosec", result))

    print(f"\n--- Done — {len(results)} episodes generated ---")

    behavioral_results = [r for t, r in results if t == "behavioral"]
    infosec_results = [r for t, r in results if t == "infosec"]

    if behavioral_results:
        behavioral_path = os.path.join(DATA_DIR, "behavioral_episodes.json")
        with open(behavioral_path, "w") as f:
            json.dump(behavioral_results, f, indent=2)
        print(f"  Behavioral episodes: {behavioral_path}")

    if infosec_results:
        infosec_path = os.path.join(DATA_DIR, "infosec_episodes.json")
        with open(infosec_path, "w") as f:
            json.dump(infosec_results, f, indent=2)
        print(f"  Infosec episodes: {infosec_path}")

    for t, r in results:
        print(f"  #{r['id']}: {r['duration']} ({r['words']} words, {r['file_size_bytes']/(1024*1024):.1f} MB)")


if __name__ == "__main__":
    main()
