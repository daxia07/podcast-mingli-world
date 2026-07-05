#!/usr/bin/env python3
"""generate.py — Build 30-minute episode script from plan.json, run edge-tts.

Each episode covers 6 patterns, 3 tips, article discussion, deep dive, common mistakes,
cultural context, practice prompts, review, quick wins. Target: ~3000 words at 130 wpm = ~25-30 min.
"""

import json, os, sys, subprocess, shutil, random
from datetime import datetime, timezone

from r2_utils import get_json

VOICE = "en-US-ChristopherNeural"


def load_patterns(content_bank, primary_id):
    """Pick 4 patterns: the primary + 3 others from different categories."""
    all_patterns = content_bank["patterns"]
    primary = all_patterns[0]
    selected = [primary]

    for p in all_patterns:
        if p["id"] == primary_id:
            primary = p
            selected = [primary]
            break

    # Add 5 more from different categories
    used_cats = {primary["category"]}
    for p in all_patterns:
        if p["category"] not in used_cats and p["id"] not in [s["id"] for s in selected]:
            selected.append(p)
            used_cats.add(p["category"])
            if len(selected) >= 6:
                break

    # Fill remaining if we don't have 6
    while len(selected) < 6:
        for p in all_patterns:
            if p["id"] not in [s["id"] for s in selected]:
                selected.append(p)
                break

    return selected


def load_tips(content_bank, primary_id):
    """Pick 2 tips: the primary + 1 from a different category."""
    all_tips = content_bank["tips"]
    primary = all_tips[0]
    selected = [primary]

    for t in all_tips:
        if t["id"] == primary_id:
            primary = t
            selected = [primary]
            break

    used_cats = {primary["category"]}
    for t in all_tips:
        if t["category"] not in used_cats:
            selected.append(t)
            used_cats.add(t["category"])
            if len(selected) >= 3:
                break

    while len(selected) < 3:
        for t in all_tips:
            if t["id"] not in [s["id"] for s in selected]:
                selected.append(t)
                break

    return selected


def build_script(plan, article, patterns, tips, content_bank):
    """Build a 30-minute episode script."""
    today = datetime.now(timezone.utc)
    ep_num = plan['episode_id']
    lines = []

    # ── INTRO (1 min) ──
    lines.append(f"Welcome to Daily Interview English. Episode {ep_num}, {today.strftime('%B %d, %Y')}.")
    lines.append("")
    lines.append("I'm your host, and this is your daily 30-minute practice session for software engineers preparing for English-language interviews.")
    lines.append("")
    lines.append("Here's what we're covering today. Six English patterns you can use in real engineering conversations. Three interview frameworks to structure your answers. A discussion of today's article. A deep dive into one pattern with multiple real-world scenarios. And a review of patterns from earlier this week.")
    lines.append("")
    lines.append("Let's get started.")
    lines.append("")

    # ── ARTICLE DISCUSSION (4 min) ──
    if article and article.get("source", {}).get("title", "") != "No article available today":
        lines.append("── Today's Article ──")
        lines.append("")
        lines.append(f"Today's episode draws from {article['source'].get('feed', 'the news')}: \"{article['source']['title']}\".")
        lines.append("")
        summary = article['source'].get('summary', '')[:600]
        lines.append(f"{summary}")
        lines.append("")
        lines.append("Let me pull out the communication lesson from this. When engineers write or speak about their work, the most effective ones do something interesting: they lead with the problem, not the solution. They make you feel the pain before they show you the fix. Watch for this pattern when you read engineering blogs or listen to tech talks. The best communicators are almost always the ones who are best at framing problems, not just describing solutions.")
        lines.append("")
        lines.append("The patterns we're practicing today are exactly this — they help you frame your thinking in a way that makes others want to engage, rather than just nod and move on.")
        lines.append("")

    # ── PATTERNS (6 patterns × 2.5 min = 15 min) ──
    for i, pat in enumerate(patterns, 1):
        lines.append(f"── Pattern {i} of {len(patterns)}: \"{pat['phrase']}\" ──")
        lines.append("")
        lines.append(f"{pat['explanation']}")
        lines.append("")

        if "when_to_use" in pat:
            lines.append(f"When to use this: {pat['when_to_use']}.")
            lines.append("")

        # Context introduction
        category_intros = {
            "opinion": "In engineering discussions, stating your opinion clearly while remaining collaborative is crucial. Here's how this pattern works in real situations.",
            "self-description": "When you're describing yourself or your career, how you phrase things matters as much as what you say. Watch how this pattern transforms a generic statement into something that sticks.",
            "transitional": "Smooth transitions between ideas are what separate fluent speakers from those who sound choppy. This pattern is one of the most versatile connectors in professional English.",
            "refining": "The ability to refine your thoughts mid-sentence shows intellectual rigor. This pattern lets you sharpen a point without starting over.",
            "impact": "Numbers without narrative are forgettable. Narrative without numbers is unconvincing. This pattern combines both to make your impact undeniable.",
            "bridging": "Nobody knows everything. The strongest engineers aren't the ones with all the answers — they're the ones who know how to handle gaps gracefully.",
            "emphasis": "In a sea of details, you need to help your listener know what matters. This pattern directs attention like a spotlight.",
            "elaboration": "Abstract claims need concrete anchors. This pattern turns 'I built a tool' into a story the interviewer can see and remember.",
            "thinking-time": "The pause before you speak can be more powerful than the words themselves. This pattern buys you time without sounding lost."
        }
        intro = category_intros.get(pat.get("category", ""), "Let me show you how this works in practice.")
        lines.append(intro)
        lines.append("")

        # Examples with full context
        examples = pat.get("examples", [])
        if examples:
            lines.append(f"I'll give you {min(4, len(examples))} examples. After each one, I'll pause so you can repeat it out loud. Pay attention to the rhythm — where the stress falls, where the pauses are.")
            lines.append("")

            for j, ex in enumerate(examples[:4], 1):
                lines.append(f"Example {j}. {ex}")
                lines.append("")
                lines.append("Say it now. Match the rhythm and intonation.")
                lines.append("")

        # Why this works
        lines.append("Why this pattern works: it signals emotional intelligence and intellectual rigor at the same time. You're not just saying words — you're demonstrating that you've thought about how your message will land.")
        lines.append("")

    # ── DEEP DIVE (5 min) ──
    primary = patterns[0]
    lines.append(f"── Deep Dive: \"{primary['phrase']}\" ──")
    lines.append("")
    lines.append(f"Let's spend a few extra minutes on today's primary pattern: \"{primary['phrase']}\"")
    lines.append("")
    lines.append(f"{primary.get('explanation', '')}")
    lines.append("")
    lines.append("I want you to understand not just what to say, but why this specific phrasing works at a psychological level.")
    lines.append("")
    lines.append("When you use this pattern in an interview or meeting, three things happen. First, you signal that you've prepared and thought about this. Second, you create space for the other person to respond without feeling defensive. Third, you demonstrate what psychologists call 'cognitive flexibility' — the ability to hold your own perspective while acknowledging other viewpoints.")
    lines.append("")
    lines.append("Let me give you two more scenarios where this pattern shines.")
    lines.append("")

    # Extra scenarios for deep dive
    deep_dive_scenarios = {
        "opinion": [
            "Scenario one: You're in a system design interview and the interviewer asks why you chose a particular database. Instead of saying 'I picked Postgres,' you say, 'The way I see it is, Postgres gives us strong consistency guarantees without the operational complexity of a distributed store at our current scale.' Notice how this transforms a simple choice into a reasoned decision.",
            "Scenario two: You're in a code review and a colleague suggests a different approach. Instead of rejecting it, you say, 'The way I see it is, both approaches handle the happy path. The difference is how they behave under failure — and that's where my concern is.' This reframes the discussion from 'my way vs your way' to 'let's think about failure modes together.'"
        ],
        "self-description": [
            "Scenario one: An interviewer asks why you moved from backend to platform engineering. Instead of 'I wanted a change,' you say 'What clicked for me was realizing that the problems I found most interesting weren't about individual services — they were about how services composed together at scale.' This shows self-awareness and strategic career thinking.",
            "Scenario two: A colleague asks why you volunteered for a tricky migration project. 'What clicked for me was that this migration was blocking three other teams. Fixing this one thing would unblock fifteen engineers.' This shows you think about impact beyond your own work."
        ]
    }
    default_scenarios = [
        "Scenario one: You're in a meeting with your manager discussing project timelines. Instead of just listing dates, use this pattern to frame your reasoning. It transforms you from a reporter of facts to a strategic thinker.",
        "Scenario two: You're explaining a technical decision to a non-technical stakeholder. This pattern helps you bridge the gap between technical accuracy and business relevance."
    ]
    scenarios = deep_dive_scenarios.get(primary.get("category", ""), default_scenarios)
    for s in scenarios:
        lines.append(s)
        lines.append("")

    lines.append("The key takeaway: great communication isn't about having the perfect words. It's about having reliable patterns you can reach for under pressure. \"{primary['phrase']}\" is one of those patterns. Make it yours.")
    lines.append("")

    # ── TIPS (3 tips × 3 min = 9 min) ──
    for i, tip in enumerate(tips, 1):
        lines.append(f"── Framework {i} of {len(tips)}: {tip['name']} ──")
        lines.append("")
        lines.append(f"{tip['explanation']}")
        lines.append("")

        segments = tip.get("segments", [])
        if segments:
            lines.append("Let me walk you through this step by step.")
            lines.append("")
            for j, seg in enumerate(segments, 1):
                lines.append(f"Step {j}. {seg}")
                lines.append("")

        lines.append(f"This framework is from {tip.get('category', 'interview research')}. I've included the source on the landing page at podcast dot mingli dot world.")
        lines.append("")

    # ── COMMON MISTAKES (3 min) ──
    lines.append("── Common Mistakes ──")
    lines.append("")
    lines.append("Let me share three mistakes I see engineers make with today's patterns, and how to avoid them.")
    lines.append("")

    primary_pat = patterns[0]
    lines.append(f"Mistake 1: Rushing through \"{primary_pat['phrase']}\" without the pause. When you say this phrase and immediately launch into your point, it sounds like you're nervous. The pause after the phrase is part of the pattern. It signals: I'm about to say something worth hearing.")
    lines.append("")
    lines.append("Practice this now: say \"{primary_pat['phrase']}\" and then count to two silently before continuing. That two-second pause transforms how the listener receives your words.")
    lines.append("")

    if len(patterns) > 1:
        second_pat = patterns[1]
        lines.append(f"Mistake 2: Overusing \"{second_pat['phrase']}\" in every sentence. These patterns are spices, not the main dish. Use them once per conversation, maybe twice. More than that and you sound like you're reading from a script rather than having a genuine conversation.")
        lines.append("")
        lines.append("The goal isn't to replace your natural communication style. It's to have these patterns available when you need them — like tools in a toolbox, not a uniform you wear every day.")
        lines.append("")

    if len(patterns) > 2:
        third_pat = patterns[2]
        lines.append(f"Mistake 3: Using \"{third_pat['phrase']}\" without actually having a clear opinion behind it. The pattern gives you the structure, but you still need to fill it with substance. Before you use it, ask yourself: what am I actually trying to say here? If you can't answer that in one sentence, don't use the pattern yet.")
        lines.append("")

    lines.append("The best communicators use these patterns so naturally that you don't notice them. That's the level we're aiming for. It takes practice, but that's exactly what these daily episodes are for.")
    lines.append("")

    # ── CULTURAL NOTE (2 min) ──
    lines.append("── Cultural Context ──")
    lines.append("")
    lines.append("A quick note about how these patterns land in different engineering cultures.")
    lines.append("")
    lines.append("In American and Australian tech companies, direct communication is valued. Patterns like \"The way I see it is\" and \"I'd argue that\" signal confidence and are generally well-received. You're expected to have opinions and express them.")
    lines.append("")
    lines.append("In many Asian and European engineering cultures, the same directness might need to be softened slightly. You might add a brief acknowledgment before stating your view. For example: \"That's an interesting perspective. The way I see it is, we might also want to consider...\"")
    lines.append("")
    lines.append("The key is calibration. Watch how senior engineers in your specific company communicate. Do they state opinions directly? Do they preface with questions? Do they use data first and opinions second? Match your approach to the culture you're in, while keeping the underlying pattern structure.")
    lines.append("")
    lines.append("This cultural awareness is itself a valuable skill. It shows you can adapt your communication style to different audiences — which is exactly what Staff and Principal engineers do every day.")
    lines.append("")

    # ── PRACTICE PROMPTS (3 min) ──
    lines.append("── Your Practice Prompts ──")
    lines.append("")
    lines.append("Now it's your turn. I'll give you two prompts. After each one, pause this episode and answer out loud. Use the patterns and frameworks from today's episode.")
    lines.append("")

    # Primary prompt from plan
    lines.append(f"Prompt 1: {plan.get('prompt_text', 'Tell me about a technical decision you made and how you communicated it to your team.')}")
    lines.append("")
    lines.append("Pause now and answer. I'll give you 10 seconds.")
    lines.append("")

    # Secondary prompt based on patterns
    prompt2 = "Tell me about a time you had to explain a complex technical trade-off to a non-technical stakeholder."
    lines.append(f"Prompt 2: {prompt2}")
    lines.append("")
    lines.append("Pause now and answer. Use at least one of today's patterns in your response.")
    lines.append("")

    # ── REVIEW SECTION (3 min) ──
    lines.append("── Weekly Review ──")
    lines.append("")
    lines.append("Let's quickly review the patterns from the last few days. I'll say the pattern phrase, and you say one original sentence using it. Ready?")
    lines.append("")

    # Get patterns from manifest for review
    manifest = get_json("manifest.json")
    reviewed = []
    if manifest:
        recent = manifest.get("episodes", [])[-5:-1]  # previous 4 episodes
        for ep in reversed(recent):
            pid = ep.get("pattern_id", "")
            for p in content_bank["patterns"]:
                if p["id"] == pid and p["id"] not in reviewed:
                    reviewed.append(p["id"])
                    lines.append(f"From episode {ep['id']}: \"{p['phrase']}\" — say your own sentence now.")
                    lines.append("")
                    break

    if not reviewed:
        lines.append("No previous episodes to review yet. Today is a great day to start building your pattern library. After you finish this episode, go to the patterns tab on the landing page and browse all 11 patterns. Pick three that feel most useful for your current situation and practice them out loud.")
        lines.append("")

    # ── QUICK WINS (2 min) ──
    lines.append("── Quick Wins for Today ──")
    lines.append("")
    lines.append("Before we wrap up, here are three things you can do right now to immediately improve your English communication in engineering settings.")
    lines.append("")
    lines.append(f"Quick win 1: In your next standup or status update, use \"{patterns[0]['phrase']}\" once. Just once. Notice how it changes the response you get compared to your usual phrasing.")
    lines.append("")
    if len(patterns) > 1:
        lines.append(f"Quick win 2: When someone disagrees with you today in a meeting or code review, try using \"{patterns[1]['phrase']}\" instead of your automatic response. The first time will feel unnatural. That's normal. The fifth time, it'll start to feel like you.")
        lines.append("")
    lines.append("Quick win 3: Listen for patterns in how senior engineers at your company communicate. What phrases do they use to state opinions? To disagree? To redirect? Write down three you hear today. Building your own pattern library starts with noticing what already works around you.")
    lines.append("")

    # ── LISTENER QUESTIONS (2 min) ──
    lines.append("── You Asked ──")
    lines.append("")
    lines.append("Here's a question I get a lot: 'How long does it take for these patterns to feel natural?'")
    lines.append("")
    lines.append("The honest answer: about two to three weeks of daily practice for each pattern. The first few times you use it, you'll feel self-conscious. You might stumble. That's not failure — that's learning. By day five or six, the pattern starts to feel familiar. By day ten, you'll catch yourself using it without thinking. That's when you know it's yours.")
    lines.append("")
    lines.append("Another common question: 'What if I use a pattern and it doesn't work — the other person reacts badly?'")
    lines.append("")
    lines.append("This happens, and it's usually about calibration, not the pattern itself. If someone reacts negatively to 'The way I see it is,' it might be because you used it in a situation where a more collaborative opening would work better. The fix isn't to abandon the pattern. It's to calibrate. Try adding an acknowledgment first: 'I hear what you're saying. The way I see it is, we might also consider...'")
    lines.append("")
    lines.append("Communication is iterative. Every conversation is data. Pay attention to what lands well and adjust. That's what the feedback buttons on the landing page are for — they help me calibrate future episodes to what works for you.")
    lines.append("")

    # ── OUTRO (1 min) ──
    lines.append("── Wrap Up ──")
    lines.append("")
    lines.append(f"That's episode {ep_num}. Here's what we covered today.")
    lines.append("")
    for i, pat in enumerate(patterns, 1):
        lines.append(f"Pattern {i}: \"{pat['phrase']}\" — {pat.get('explanation', '')[:100]}")
    lines.append("")
    for i, tip in enumerate(tips, 1):
        lines.append(f"Framework {i}: {tip['name']}")
    lines.append("")

    lines.append("Your action items for today:")
    lines.append(f"1. Use \"{patterns[0]['phrase']}\" at least three times in real conversation today.")
    lines.append("2. Practice both prompts out loud until your answers feel natural.")
    lines.append("3. Go to podcast dot mingli dot world and press thumbs up or thumbs down. Your feedback directly shapes tomorrow's episode.")
    lines.append("")
    lines.append("Great work today. Consistent practice over time is what builds real fluency. See you tomorrow.")
    lines.append("")

    return "\n".join(lines)


def run_edge_tts(script_text, output_path):
    """Generate MP3 at interview pace (slower, clearer)."""
    script_path = "/tmp/episode_script_long.txt"
    with open(script_path, "w") as f:
        f.write(script_text)

    # Slightly slower rate for clearer delivery (~130 wpm instead of ~150 wpm)
    cmd = ["edge-tts", "--voice", VOICE, "--rate=-15%", "--text", script_text, "--write-media", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Fallback: file-based
        cmd2 = ["edge-tts", "--voice", VOICE, "--rate=-15%", "-f", script_path, "--write-media", output_path]
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        if result2.returncode != 0:
            raise RuntimeError(f"edge-tts failed: {result2.stderr}")

    # Post-process with ffmpeg if available
    if shutil.which("ffmpeg"):
        temp_path = output_path + ".temp.mp3"
        os.rename(output_path, temp_path)
        subprocess.run([
            "ffmpeg", "-y", "-i", temp_path,
            "-af", "loudnorm, silenceremove=stop_periods=-1:stop_duration=0.3:stop_threshold=-40dB",
            output_path
        ], capture_output=True)
        os.remove(temp_path)


def main():
    print("=== generate.py (30-min episodes) ===")

    # Load plan from R2
    print("Loading plan.json...")
    plan = get_json("plan.json")
    if not plan:
        print("ERROR: No plan.json found. Run arrange.py first.")
        sys.exit(1)

    # Load today.json if available
    script_dir = os.path.dirname(os.path.abspath(__file__))
    today_json = os.path.join(os.path.dirname(script_dir), "data", "today.json")
    article = None
    if os.path.exists(today_json):
        with open(today_json) as f:
            article = json.load(f)

    # Load content bank
    with open(os.path.join(script_dir, "content_bank.json")) as f:
        content_bank = json.load(f)

    # Select 4 patterns and 2 tips
    patterns = load_patterns(content_bank, plan["pattern_id"])
    tips = load_tips(content_bank, plan["tip_id"])

    print(f"  Episode #{plan['episode_id']}")
    print(f"  Patterns:")
    for p in patterns:
        print(f"    - \"{p['phrase']}\" ({p['category']})")
    print(f"  Tips:")
    for t in tips:
        print(f"    - {t['name']} ({t['category']})")

    # Build script
    print("Building 30-minute episode script...")
    script = build_script(plan, article, patterns, tips, content_bank)
    word_count = len(script.split())
    print(f"  Script: {len(script)} chars, ~{word_count} words")
    print(f"  Estimated duration: ~{word_count / 140:.0f} minutes")

    # Generate audio
    output_dir = os.path.join(os.path.dirname(script_dir), "data")
    os.makedirs(output_dir, exist_ok=True)
    mp3_path = os.path.join(output_dir, "episode.mp3")
    script_path = os.path.join(output_dir, "script.txt")

    with open(script_path, "w") as f:
        f.write(script)

    print("Generating audio with edge-tts (this may take 2-3 minutes for 30 min of content)...")
    run_edge_tts(script, mp3_path)

    size_mb = os.path.getsize(mp3_path) / (1024 * 1024)
    print(f"  MP3: {size_mb:.1f} MB")
    print("Done")


if __name__ == "__main__":
    main()
