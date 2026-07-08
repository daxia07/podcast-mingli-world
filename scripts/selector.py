#!/usr/bin/env python3
"""selector.py — Query tutor DB for due concepts, enrich with content_bank,
write plan.json + script.txt for generate.py. Bridges spaced repetition
progress to podcast content production.

Usage:
  python3 scripts/selector.py --topic system-design [--count 3] [--dry-run]
  python3 scripts/selector.py --topic coding-interview [--count 3]
  python3 scripts/selector.py --topic interview-english [--count 6]
"""

import json, os, sys, sqlite3, argparse
from datetime import datetime, timezone


TUTOR_DB = os.path.expanduser("~/projects/generic-tutor/data/tutor.db")
CONTENT_BANK_PATH = os.path.join(os.path.dirname(__file__), "content_bank.json")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
KNOWLEDGE_DIR = os.path.expanduser("~/projects/generic-tutor/knowledge")


def load_content_bank():
    with open(CONTENT_BANK_PATH) as f:
        return json.load(f)


def get_due_concepts(topic_id, limit=4):
    """Query tutor DB for concepts due for review, ordered by priority."""
    conn = sqlite3.connect(TUTOR_DB)
    conn.row_factory = sqlite3.Row
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    rows = conn.execute(
        """SELECT id, title, status, ef, interval, repetitions, next_review,
                  last_grade, difficulty, prerequisites
           FROM concepts
           WHERE topic_id = ?
             AND (next_review <= ? OR next_review IS NULL)
           ORDER BY
             CASE status
               WHEN 'learning' THEN 0
               WHEN 'unseen' THEN 1
               WHEN 'reviewing' THEN 2
               ELSE 3
             END,
             ef ASC,
             next_review ASC
           LIMIT ?""",
        (topic_id, today, limit),
    ).fetchall()

    conn.close()
    return [dict(r) for r in rows]


def get_topic_summary(topic_id):
    """Get topic-level stats for the intro."""
    conn = sqlite3.connect(TUTOR_DB)
    conn.row_factory = sqlite3.Row

    topic = dict(conn.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone() or {})
    if not topic:
        conn.close()
        return None

    concepts = conn.execute(
        "SELECT status, COUNT(*) as c FROM concepts WHERE topic_id = ? GROUP BY status",
        (topic_id,),
    ).fetchall()

    summary = {"name": topic.get("name", topic_id), "phase": topic.get("phase", 1)}
    for row in concepts:
        summary[row["status"]] = row["c"]
    conn.close()
    return summary


def find_content_bank_match(concept_id, content_bank, topic):
    """Match a tutor concept to content_bank entries."""
    if topic == "system-design":
        # Try core_concepts, case_studies, architecture_patterns
        for section in ["core_concepts", "case_studies", "architecture_patterns"]:
            for entry in content_bank.get("system_design", {}).get(section, []):
                if entry["id"] == concept_id or concept_id in entry.get("id", ""):
                    return entry
    elif topic == "coding-interview":
        for entry in content_bank.get("coding_interview", {}).get("patterns", []):
            if entry.get("id") == concept_id:
                return entry
    return None


def read_concept_markdown(topic_id, concept_id):
    """Read the concept markdown file, stripping YAML frontmatter if present."""
    # Try topic-specific directory layout
    candidates = [
        os.path.join(KNOWLEDGE_DIR, topic_id, "concepts", f"{concept_id}.md"),
        os.path.join(KNOWLEDGE_DIR, topic_id, f"{concept_id}.md"),
        os.path.join(KNOWLEDGE_DIR, "concepts", f"{concept_id}.md"),
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path) as f:
                raw = f.read()
            # Strip YAML frontmatter if present
            if raw.startswith("---"):
                end = raw.find("\n---", 3)
                if end != -1:
                    raw = raw[end + 4:].strip()
            return raw
    return None


def build_script_text(topic_id, concepts, summary, content_bank):
    """Generate a podcast script from due concepts and content bank data."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    topic_name = summary.get("name", topic_id.replace("-", " ").title())

    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"{topic_name} Playlist — Auto-generated Episode")
    lines.append(f"Date: {today}")
    lines.append(f"Concepts: {', '.join(c['title'] for c in concepts)}")
    lines.append(f"{'='*60}")
    lines.append("")

    # Intro
    lines.append("[INTRO — 30 sec]")
    lines.append("")
    mastered = summary.get("mastered", 0)
    learning = summary.get("learning", 0)
    total = sum(v for k, v in summary.items() if k in ("unseen", "learning", "reviewing", "mastered"))
    lines.append(
        f"Welcome to the {topic_name} Playlist. You're in phase {summary.get('phase', 1)} "
        f"with {mastered} concepts mastered out of {total}. "
        f"Today we're reviewing {len(concepts)} concepts that are due for spaced repetition."
    )
    lines.append("")
    lines.append("")

    for i, concept in enumerate(concepts):
        title = concept["title"]
        cid = concept["id"]
        status = concept["status"]
        difficulty = concept.get("difficulty", 3)

        segment_num = i + 1
        duration = max(2, 5 - difficulty)  # easier = shorter segment

        lines.append(f"{'='*60}")
        lines.append(f"SEGMENT {segment_num}: {title.upper()}")
        lines.append(f"{'='*60}")
        lines.append("")
        lines.append(f"[{duration} min]")
        lines.append("")

        # Read concept markdown for content
        md = read_concept_markdown(topic_id, cid)
        if md:
            # Extract key sections
            sections = {}
            current_section = None
            for line in md.split("\n"):
                if line.startswith("## "):
                    current_section = line[3:].strip().lower()
                    sections[current_section] = []
                elif current_section:
                    sections[current_section].append(line)

            # Use available sections (try preferred names first, then any section with content)
            found_section = False
            for sec_name in ["definition", "summary", "key terms", "key points", "core concepts", "overview"]:
                if sec_name in sections:
                    content = "\n".join(sections[sec_name])
                    content = content.replace("**", "").replace("###", "").strip()
                    if content:
                        lines.append(content)
                        lines.append("")
                        found_section = True
                        break
            # Fallback: first non-empty section
            if not found_section:
                for sec_name, sec_lines in sections.items():
                    content = "\n".join(sec_lines).replace("**", "").replace("###", "").strip()
                    if content and len(content) > 50:
                        lines.append(content[:800])
                        lines.append("")
                        break

            # Why it matters
            if "why it matters" in sections:
                lines.append("Here's why this matters in interviews:")
                lines.append("")
                for line in sections["why it matters"]:
                    cleaned = line.strip().lstrip("- ").replace("**", "")
                    if cleaned:
                        lines.append(cleaned)
                lines.append("")

            # Gotchas
            if "gotchas" in sections:
                lines.append("Common mistakes to avoid:")
                lines.append("")
                for line in sections["gotchas"]:
                    cleaned = line.strip().lstrip("- ").replace("**", "")
                    if cleaned:
                        lines.append(f"• {cleaned}")
                lines.append("")

            # Interview questions
            if "interview questions" in sections:
                lines.append("Practice this:")
                lines.append("")
                for line in sections["interview questions"]:
                    cleaned = line.strip().lstrip("123456789. ").replace("**", "")
                    if cleaned and cleaned.startswith('"'):
                        lines.append(f"• {cleaned}")
                lines.append("")

        # Also check content_bank for enrichment
        bank_match = find_content_bank_match(cid, content_bank, topic_id)
        if bank_match:
            if "trade_offs" in bank_match and isinstance(bank_match["trade_offs"], str):
                lines.append(f"Key trade-off: {bank_match['trade_offs'][:300]}")
                lines.append("")
            if "real_examples" in bank_match and isinstance(bank_match["real_examples"], str):
                lines.append(f"Real-world example: {bank_match['real_examples'][:300]}")
                lines.append("")

        # SM-2 context
        if status == "learning":
            lines.append(f"This concept is in your learning queue. You last rated it {concept.get('last_grade', '?')}/5. Keep practicing.")
        elif status == "reviewing":
            lines.append(f"This concept is in spaced review. Your easiness factor is {concept.get('ef', 2.5):.1f}. Review it to build mastery.")
        elif status == "unseen":
            lines.append("This is a new concept. Listen for the big idea first, then come back for details in later episodes.")

        lines.append("")
        lines.append("")

    # Review segment
    lines.append(f"{'='*60}")
    lines.append("REVIEW — Quick Recap")
    lines.append(f"{'='*60}")
    lines.append("")
    lines.append("[1 min 30 sec]")
    lines.append("")
    lines.append("Quick recap of today's concepts:")
    lines.append("")
    for i, c in enumerate(concepts):
        lines.append(f"{i+1}. {c['title']} — due for review. Status: {c['status']}.")
    lines.append("")
    lines.append("Your tutor tracks your progress on each of these. Grade yourself 0-5")
    lines.append("after this episode to update your spaced repetition schedule.")
    lines.append("")

    # Next episode preview
    lines.append(f"{'='*60}")
    lines.append("NEXT EPISODE PREVIEW")
    lines.append(f"{'='*60}")
    lines.append("")

    # Query what unlocks after these concepts
    conn = sqlite3.connect(TUTOR_DB)
    placeholders = ",".join("?" for _ in concepts)
    prereq_ids = [c["id"] for c in concepts]
    next_concepts = conn.execute(
        f"""SELECT id, title FROM concepts
            WHERE topic_id = ?
              AND id NOT IN ({placeholders})
              AND status = 'unseen'
            ORDER BY difficulty ASC
            LIMIT 3""",
        [topic_id] + prereq_ids,
    ).fetchall()
    conn.close()

    if next_concepts:
        lines.append("After mastering today's concepts, you'll unlock:")
        for nc in next_concepts:
            lines.append(f"  • {nc[1]}")
    lines.append("")

    lines.append("Until next time. Keep learning.")
    lines.append("")

    return "\n".join(lines)


def write_plan_json(concepts, topic_id, episode_num):
    """Write plan.json in the format generate.py expects."""
    today = datetime.now(timezone.utc)
    plan = {
        "episode_id": episode_num,
        "date": today.strftime("%Y-%m-%d"),
        "topic": topic_id,
        "concepts": [
            {
                "id": c["id"],
                "title": c["title"],
                "status": c["status"],
                "difficulty": c.get("difficulty", 3),
            }
            for c in concepts
        ],
        "generated_by": "selector.py",
        "generated_at": today.isoformat(),
    }

    # generate.py expects pattern_id, tip_id — for system-design/coding,
    # use concept IDs
    if concepts:
        plan["primary_concept_id"] = concepts[0]["id"]
        plan["primary_concept_title"] = concepts[0]["title"]

    os.makedirs(DATA_DIR, exist_ok=True)
    plan_path = os.path.join(DATA_DIR, "plan.json")
    with open(plan_path, "w") as f:
        json.dump(plan, f, indent=2)
    return plan_path


def main():
    parser = argparse.ArgumentParser(description="Select due concepts and generate podcast plan")
    parser.add_argument("--topic", required=True, help="Topic ID (e.g., system-design)")
    parser.add_argument("--count", type=int, default=3, help="Max concepts per episode")
    parser.add_argument("--dry-run", action="store_true", help="Print script only, don't write files")
    args = parser.parse_args()

    # Get tutor progress
    summary = get_topic_summary(args.topic)
    if not summary:
        print(f"ERROR: Topic '{args.topic}' not found in tutor DB.")
        print("Available topics:")
        conn = sqlite3.connect(TUTOR_DB)
        for row in conn.execute("SELECT id, name FROM topics"):
            print(f"  {row[0]}: {row[1]}")
        conn.close()
        sys.exit(1)

    concepts = get_due_concepts(args.topic, args.count)
    if not concepts:
        print(f"No concepts due for '{args.topic}'. You're all caught up!")
        sys.exit(0)

    print(f"Topic: {summary['name']} (phase {summary.get('phase', 1)})")
    print(f"Due concepts: {len(concepts)}")
    for c in concepts:
        print(f"  • {c['title']} [{c['status']}, ef={c.get('ef', 2.5):.1f}]")

    # Load content bank
    content_bank = load_content_bank()

    # Generate script
    script = build_script_text(args.topic, concepts, summary, content_bank)

    if args.dry_run:
        print("\n" + "=" * 60)
        print("GENERATED SCRIPT (dry run)")
        print("=" * 60)
        print(script)
        return

    # Write script.txt
    os.makedirs(DATA_DIR, exist_ok=True)
    script_path = os.path.join(DATA_DIR, "script.txt")
    with open(script_path, "w") as f:
        f.write(script)
    print(f"\nScript written: {script_path} ({len(script)} chars)")

    # Determine episode number
    conn = sqlite3.connect(TUTOR_DB)
    episode_num = 1
    plan_path = write_plan_json(concepts, args.topic, episode_num)
    print(f"Plan written: {plan_path}")

    print("\nNext steps:")
    print(f"  cd ~/projects/podcast-mingli-world")
    print(f"  python3 scripts/generate.py     # edge-tts → episode.mp3")
    print(f"  python3 scripts/publish.py      # upload to R2 + update manifest")


if __name__ == "__main__":
    main()
