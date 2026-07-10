#!/usr/bin/env python3
"""generate_estimation.py — Back-of-envelope estimation practice episodes.

Voice: en-US-EmmaNeural (cheerful, clear, good for numbers)
Duration: 10-12 min per episode
3-4 estimation problems per episode
Each: state assumptions → step-by-step calculation → sanity check → design implications
"""

import json, os, sys, subprocess, shutil, tempfile
from datetime import datetime, timezone

from tts import synthesize, get_duration_str

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

ESTIMATION_EPISODES = [
    {
        "id": 44, "theme": "estimation-1",
        "title": "Estimation Practice I",
        "subtitle": "Twitter QPS, Google storage, WhatsApp bandwidth",
        "playlist_id": "sd-estimation",
        "problems": [
            {
                "name": "Twitter QPS and Storage",
                "prompt": "Estimate the queries per second and storage for Twitter.",
                "assumptions": [
                    "1.5 billion total users",
                    "300 million daily active users",
                    "Each user posts 2 tweets per day on average",
                    "Average tweet is 200 bytes of text plus one 500KB image, 20% of tweets have images",
                    "10:1 read-to-write ratio",
                ],
                "calculation": [
                    "Write QPS: 300 million DAU times 2 tweets per day equals 600 million tweets per day. 600 million divided by 86,400 seconds gives us about 7,000 tweets per second. With a safety margin of 2x for peak, that's 14,000 write QPS.",
                    "Read QPS: 10 times the write QPS, so 70,000 reads per second at average, 140,000 at peak.",
                    "Storage per day: 600 million tweets times 200 bytes is 120 gigabytes of text per day. For images: 20 percent of 600 million is 120 million images, times 500KB each, that's 60 terabytes per day. So total is about 60 terabytes per day.",
                    "Annual storage: 60 terabytes per day times 365 days is about 22 petabytes per year.",
                ],
                "sanity_check": "Let me sanity check this. YouTube uploads about 500 hours of video per minute, which is way more data than Twitter. And Google processes about 8.5 billion searches per day, which is about 100,000 QPS — similar order of magnitude to our read QPS. So these numbers seem reasonable.",
                "implications": "So what does this mean for the design? At 70,000 read QPS, we definitely need caching — a single database can't handle that. At 60 terabytes per day of storage, we need object storage for images, not a relational database. And at 14,000 write QPS, we need to shard the tweet database, probably by user ID.",
            },
            {
                "name": "Google Storage for Web Index",
                "prompt": "How much storage does Google need to index the web?",
                "assumptions": [
                    "About 50 billion web pages",
                    "Average web page is 1 megabyte of HTML, CSS, and JavaScript",
                    "But Google stores a compressed version — about 100KB per page",
                    "Index metadata adds another 50KB per page",
                    "3 copies of everything for redundancy",
                ],
                "calculation": [
                    "Raw storage: 50 billion pages times 100KB per page is 5 petabytes of compressed content.",
                    "Index metadata: 50 billion times 50KB is 2.5 petabytes.",
                    "Total per copy: 7.5 petabytes. With 3 copies, that's about 22.5 petabytes.",
                    "But Google also stores cached versions, search logs, and ML training data. Real estimates put Google's total storage in the hundreds of exabytes range. This is just the web index portion.",
                ],
                "sanity_check": "Amazon S3 is estimated to store over 100 trillion objects. If each object is 100KB on average, that's 10 exabytes. Google's index being 7.5 petabytes per copy seems very reasonable by comparison.",
                "implications": "For the design, this means we need distributed storage across thousands of machines. No single machine can hold even a fraction of the index. We'd shard by URL hash or by topic, and use a distributed file system like GFS or HDFS for the raw data.",
            },
            {
                "name": "WhatsApp Bandwidth",
                "prompt": "Estimate the daily bandwidth for WhatsApp.",
                "assumptions": [
                    "2 billion monthly active users",
                    "1 billion daily active users",
                    "Each user sends 50 messages per day",
                    "Average message is 100 bytes of text",
                    "50% of messages have a 3MB image or video attachment",
                    "Each message is delivered to an average of 2 recipients (group chats)",
                ],
                "calculation": [
                    "Messages per day: 1 billion users times 50 messages is 50 billion messages per day.",
                    "Text data: 50 billion times 100 bytes is 5 gigabytes. Tiny compared to media.",
                    "Media data: 50 percent of 50 billion is 25 billion media messages. Times 3MB each is 75 petabytes. But each is delivered to 2 recipients, so 150 petabytes of outbound bandwidth per day.",
                    "Convert to throughput: 150 petabytes divided by 86,400 seconds is about 1.7 terabytes per second of outbound bandwidth.",
                ],
                "sanity_check": "Netflix streams about 1 petabyte per hour during peak times. WhatsApp at 1.7 terabytes per second is about 6 petabytes per hour. WhatsApp has more users than Netflix, and messages are more frequent than video streams, so this seems in the right ballpark. Though many messages are text-only, which would bring the average down significantly.",
                "implications": "At 1.7 terabytes per second outbound, we absolutely need a CDN or edge distribution. Delivering all media from a central data center would be too expensive and too slow. We'd also want end-to-end encryption, which means the media is encrypted on the device and we can't cache decrypted versions at the edge — a real design tension.",
            },
        ]
    },
    {
        "id": 45, "theme": "estimation-2",
        "title": "Estimation Practice II",
        "subtitle": "Payment TPS, Netflix CDN, Uber location writes",
        "playlist_id": "sd-estimation",
        "problems": [
            {
                "name": "Payment System TPS",
                "prompt": "Estimate transactions per second for a global payment processor like Stripe.",
                "assumptions": [
                    "Processes payments for 1 million businesses",
                    "Average business does 1,000 transactions per day",
                    "Peak-to-average ratio is 3x (Black Friday, seasonal spikes)",
                    "Each transaction record is 500 bytes",
                    "Transactions are stored for 7 years for compliance",
                ],
                "calculation": [
                    "Daily transactions: 1 million businesses times 1,000 transactions is 1 billion transactions per day.",
                    "Average TPS: 1 billion divided by 86,400 seconds is about 11,500 transactions per second.",
                    "Peak TPS: 3 times that is about 35,000 transactions per second.",
                    "Daily storage: 1 billion times 500 bytes is 500 gigabytes per day.",
                    "7-year retention: 500 gigabytes times 365 times 7 is about 1.3 petabytes. Very manageable for modern storage systems.",
                ],
                "sanity_check": "Visa processes about 65,000 transactions per second at peak. Stripe is smaller than Visa but serves the long tail of internet businesses. 35,000 peak TPS seems reasonable. Amazon Prime Day processes about 100,000 orders per second at peak, which is a similar order of magnitude.",
                "implications": "At 35,000 TPS, a single database can't handle the write load. We'd need sharding, probably by merchant ID. And because payments require strong consistency — you cannot risk double-charging — each shard would use a single-leader database with synchronous replication. The ledger must be append-only and ACID-compliant.",
            },
            {
                "name": "Netflix CDN Storage",
                "prompt": "How much storage does Netflix need for its content library on CDN?",
                "assumptions": [
                    "15,000 titles in the library",
                    "Average title is 2 hours long",
                    "Encoded in 5 resolutions: 4K at 20Mbps, 1080p at 8Mbps, 720p at 5Mbps, 480p at 2Mbps, 360p at 1Mbps",
                    "CDN stores content at 200 edge locations worldwide",
                ],
                "calculation": [
                    "Storage per title: 2 hours times 3600 seconds is 7,200 seconds. Total bitrate across all encodings is 20 plus 8 plus 5 plus 2 plus 1, equals 36 megabits per second. So 7,200 seconds times 36 megabits divided by 8 bits per byte is about 32 gigabytes per title.",
                    "Total library: 15,000 titles times 32 gigabytes is 480 terabytes.",
                    "With 200 edge locations: 480 terabytes times 200 is 96 petabytes of total CDN storage. Though in practice, not every edge caches every title — popular titles are everywhere, niche titles are only at regional hubs.",
                ],
                "sanity_check": "Netflix has publicly stated they deliver over 1 petabyte of data per hour during peak times. If the entire library is 480 terabytes and they stream 1 petabyte per hour, that means the entire library is streamed roughly twice per hour. That seems very plausible for a service with 250 million subscribers.",
                "implications": "96 petabytes of CDN storage means we need intelligent caching. Not every title at every edge. We'd use a popularity-based caching policy — new releases everywhere, older content at regional hubs only. And adaptive bitrate streaming means we need smooth switching between resolutions, which requires chunked encoding.",
            },
            {
                "name": "Uber Location Writes",
                "prompt": "Estimate the write QPS for Uber's real-time location tracking.",
                "assumptions": [
                    "25 million daily active riders",
                    "5 million drivers, 60% active at any time",
                    "Active drivers report location every 5 seconds",
                    "Each location update is 50 bytes (lat, lng, timestamp, driver_id)",
                    "Riders report location every 30 seconds when in a trip",
                ],
                "calculation": [
                    "Active drivers: 5 million times 60 percent is 3 million active drivers.",
                    "Driver location writes: 3 million drivers, one update every 5 seconds, that's 600,000 writes per second.",
                    "Active riders in trip: let's say 20% of 25 million riders are in a trip at any time, that's 5 million riders. One update every 30 seconds means about 170,000 writes per second.",
                    "Total location write QPS: 600,000 plus 170,000 is about 770,000 writes per second.",
                    "Daily storage: 770,000 writes times 86,400 seconds times 50 bytes is about 3.3 terabytes per day of raw location data.",
                ],
                "sanity_check": "770,000 writes per second is a lot. But remember, this is just simple key-value writes — put driver 123's current location. No complex queries, no joins. Redis can handle over 100,000 simple writes per second per instance. So we'd need about 8 Redis shards, which is very doable.",
                "implications": "At 770,000 location writes per second, we'd use an in-memory store like Redis for real-time location, with TTL-based expiration. The writes are simple — just updating a key — so the bottleneck is network throughput, not computational complexity. For historical location data, we'd batch-write to a time-series database like InfluxDB or Cassandra.",
            },
        ]
    },
]


def build_estimation_script(episode_config):
    """Build a think-aloud estimation script."""
    lines = []

    lines.append(f"Welcome to Estimation Practice. Today we're working through {len(episode_config['problems'])} back-of-envelope estimation problems.")
    lines.append("")
    lines.append("The key to estimation is being explicit about your assumptions, showing your math step by step, and sanity-checking your answer. Let's practice.")
    lines.append("")

    for i, problem in enumerate(episode_config["problems"]):
        lines.append(f"Problem {i+1}: {problem['name']}.")
        lines.append("")
        lines.append(f"So the question is: {problem['prompt']}")
        lines.append("")

        lines.append("Let me start by stating my assumptions.")
        lines.append("")
        for j, assumption in enumerate(problem["assumptions"]):
            lines.append(f"Assumption {j+1}: {assumption}")
            lines.append("")

        lines.append("OK, now let me work through the math out loud.")
        lines.append("")
        for step in problem["calculation"]:
            lines.append(step)
            lines.append("")

        lines.append("So... let me sanity check this.")
        lines.append("")
        lines.append(problem["sanity_check"])
        lines.append("")

        lines.append("Now, what does this mean for the design? The estimation tells us what infrastructure we need.")
        lines.append("")
        lines.append(problem["implications"])
        lines.append("")

        if i < len(episode_config["problems"]) - 1:
            lines.append("Alright, let's move to the next problem.")
            lines.append("")

    lines.append("Great practice session. Remember the pattern: state assumptions clearly, show your math step by step, sanity check against known numbers, and always connect the estimation back to design implications. The interviewer doesn't expect exact numbers — they want to see structured reasoning.")
    lines.append("")
    lines.append("Keep practicing these out loud. See you next time.")
    lines.append("")

    return "\n".join(lines)


def main():
    print("=== generate_estimation.py ===")

    os.makedirs(DATA_DIR, exist_ok=True)

    theme = sys.argv[1] if len(sys.argv) > 1 else None
    configs = ESTIMATION_EPISODES
    if theme:
        configs = [c for c in configs if c["theme"] == theme]
        if not configs:
            print(f"ERROR: Unknown theme '{theme}'")
            sys.exit(1)

    results = []
    for config in configs:
        print(f"\n--- #{config['id']}: {config['title']} ---")

        script = build_estimation_script(config)
        word_count = len(script.split())
        est_min = word_count / 140
        print(f"  Script: {word_count} words, ~{est_min:.0f} min estimated")

        script_path = os.path.join(DATA_DIR, f"est-{config['theme']}.txt")
        with open(script_path, "w") as f:
            f.write(script)

        mp3_path = os.path.join(DATA_DIR, f"est-{config['theme']}.mp3")
        print(f"  Generating audio (EmmaNeural)...")
        synthesize(script, mp3_path, voice="estimation")

        size_mb = os.path.getsize(mp3_path) / (1024 * 1024)
        duration = get_duration_str(mp3_path)
        print(f"  MP3: {size_mb:.1f} MB, {duration}")

        results.append({
            "id": config["id"],
            "theme": config["theme"],
            "title": config["title"],
            "subtitle": config["subtitle"],
            "playlist_id": config["playlist_id"],
            "mp3_path": mp3_path,
            "script_path": script_path,
            "file_size_bytes": os.path.getsize(mp3_path),
            "duration": duration,
        })

    print(f"\nDone — {len(results)} estimation episodes generated")


if __name__ == "__main__":
    main()
