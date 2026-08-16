# AWS Certification Track — Materials, Plan, Podcast Roadmap

Researched 13 Aug 2026. Every exam fact below is taken from the official AWS exam guides
(`docs.aws.amazon.com/aws-certification/...`), not from blogs. Third-party claims are marked as such.

---

## 1. The three exams, verified

| | AI Practitioner | Solutions Architect – Associate | Security – Specialty |
|---|---|---|---|
| **Exam code** | **AIF-C01** | **SAA-C03** | **SCS-C03** (since 2 Dec 2025) |
| Level | Foundational | Associate | Specialty |
| Price (USD) | 100 | 150 | 300 |
| Time | 90 min | 130 min | 170 min |
| Questions | 65 (50 scored + 15 unscored) | 65 (50 + 15) | 65 (50 + 15) |
| **Pass mark** | 700 / 1000 | 720 / 1000 | 750 / 1000 |
| Question types | MC, MR, ordering, matching | MC, MR only | MC, MR, ordering, matching |
| Target candidate | ≤ 6 months AI/ML exposure on AWS | ≥ 1 yr designing on AWS | 3–5 yrs securing cloud |
| Valid for | 3 years | 3 years | 3 years |

### Domain weightings

**AIF-C01** — Fundamentals of AI & ML 20% · Fundamentals of GenAI 24% · **Applications of Foundation Models 28%** · Responsible AI 14% · Security, Compliance & Governance for AI 14%

**SAA-C03** — **Design Secure Architectures 30%** · Design Resilient Architectures 26% · Design High-Performing Architectures 24% · Design Cost-Optimized Architectures 20%

**SCS-C03** — Detection 16% · Incident Response 14% · Infrastructure Security 18% · **Identity & Access Management 20%** · Data Protection 18% · Security Foundations & Governance 14%

### Two corrections to what you'll find online

1. **There is no SAA-C04.** Several SEO blogs (e.g. citadelcloudmanagement) claim SAA-C04 launched in March 2024 and that C03 retires 30 Sep 2026. The AWS exam guide index and the AWS "Coming Soon" page both still list **SAA-C03** as the only version, with no announced successor. Ignore any course sold as "SAA-C04".
2. **Security is SCS-C03, not SCS-C02.** SCS-C02's last testable day was 1 Dec 2025. Anything you buy that says SCS-C02 is a version behind.

### What changed in SCS-C03 (matters for both study and episode content)

*Added:* generative-AI guardrails (OWASP Top 10 for LLM Applications) · OCSF-format ingestion and third-party WAF rules at the edge · inter-node encryption in transit (EMR, EKS, SageMaker AI, Nitro) · data masking (CloudWatch Logs data protection policies, SNS message data protection) · imported vs AWS-generated KMS key material · multi-Region key and certificate management (KMS CMKs, AWS Private CA) · validating findings from AWS security services to scope an event.

*Removed:* TCP/IP and OSI fundamentals · host-based firewalls/hardening · VPC Reachability Analyzer / Inspector network reachability analysis · IAM policy component basics (Principal/Action/Resource/Condition) · TLS concepts · AWS Security Finding Format (ASFF) · S3 static website hosting.

*Restructured:* old "Threat Detection & Incident Response" + "Security Logging & Monitoring" were re-cut into **Detection** and **Incident Response**. IAM went from 16% → **20%** (now the largest domain). Domain 6 renamed to "Security Foundations and Governance".

---

## 2. Order and cost

**Recommended order: AIF-C01 → SAA-C03 → SCS-C03.**

- Cheapest and fastest exam first; it produces a **50% discount voucher** for the next one (AWS gives every passer a 50% voucher in their Certification Account).
- SAA is the load-bearing one — SCS-C03 assumes you already know VPC, IAM, KMS, and Organizations cold.
- SCS-C03 is a *specialty*: AWS targets 3–5 years of cloud-security experience. Passing SAA does not make you ready; budget the most time here.

| | List price | With 50% voucher chain |
|---|---|---|
| AIF-C01 | $100 | $100 |
| SAA-C03 | $150 | $75 |
| SCS-C03 | $300 | $150 |
| **Total** | **$550** | **~$325** |

Caveats: confirm voucher terms in your AWS Certification Account before booking (they are issued on a pass, typically within 1–2 business days). AWS also runs periodic promotions — a "25% off + free retake" campaign was reported earlier in 2026 (third-party reporting, unverified). Check for an active promo before paying full price. Failed exams require a **14-day wait** before a retake, at full price.

Renewal note: certs last 3 years. A **paid Skill Builder subscription** counts as a 1-year "maintenance" extension, and passing a higher-level exam renews the lower one (e.g. SA Pro renews SAA).

---

## 3. Materials, ranked

### Tier 0 — official and free (do these for all three)

| Resource | What it is | Link |
|---|---|---|
| **Exam guide** | The actual source of truth: domains, task statements, in-scope/out-of-scope service lists | AIF: `docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/` · SAA: `.../solutions-architect-associate-03/` · SCS: `.../security-specialty-03/` |
| **Skill Builder Exam Prep course** | Free ~2-hour digital course per exam, topic areas + sample questions | `skillbuilder.aws/category/exam-prep/...` |
| **Official Practice Question Set** | Free 20-question AWS-written set — the only free questions written in the real exam's voice | Skill Builder |
| **In-scope / out-of-scope service lists** | Underused. Tells you exactly what *not* to study | Inside each exam guide |
| **AWS Cloud Quest** (free tier) | Game-based hands-on practice | Skill Builder |
| Whitepapers | Well-Architected Framework + Security Pillar (SAA); Security Best Practices, Shared Responsibility, KMS Cryptographic Details (SCS) | aws.amazon.com/whitepapers |

### Tier 1 — paid, worth it

| Resource | Cost | Verdict |
|---|---|---|
| **AWS Skill Builder subscription** | $29/mo | The **only** source of official full-length Practice Exams and Official Pretests. Buy **one month per exam, timed to the two weeks before your test** — not a standing subscription. Doubles as a 1-year cert-maintenance path. |
| **Tutorials Dojo (Jon Bonso) practice exams** | ~$15–20 per cert | The community's consistent top pick for closest-to-real questions with good explanations. **Check the SCS set is fully migrated to C03** — as of recent forum posts they were still refining it. |
| **Stephane Maarek (Udemy)** | $12–20 on sale | Best value video course for AIF-C01 and SAA-C03. Frequently updated. Don't pay list price; it's on sale constantly. |
| **Adrian Cantrill (learn.cantrill.io)** | ~$40–50 per course | Deeper and more architectural than Maarek — better if you want to actually understand rather than pass. Strong for SAA and Security. |

### Tier 2 — free video
freeCodeCamp's ~16-hour SAA-C03 course on YouTube is a legitimate free alternative to a paid video course.

### Avoid
- **Exam dumps** (dumpsgate, "real exam questions", ExamTopics-style sites). They violate the AWS Certification Agreement and can void your certifications.
- **AI-generated "2026 study guide" books on Amazon.** Several of the top results for AIF-C01 are low-quality generated content.
- **Anything labelled SCS-C02 or SAA-C04.**

---

## 4. Time budget

| Exam | Realistic prep | Shape of the work |
|---|---|---|
| AIF-C01 | 15–25 hrs over 2–3 weeks | Breadth over depth. It rewards recognising Bedrock/SageMaker/Comprehend/Rekognition use cases and responsible-AI vocabulary, not maths. |
| SAA-C03 | 60–100 hrs over 6–10 weeks | Video course once → hands-on → practice exams until consistently 80%+. Security is 30% of it, so it front-loads SCS. |
| SCS-C03 | 60–90 hrs over 6–8 weeks | IAM policy evaluation logic (SCP + permission boundary + resource policy + session policy), KMS key policies and grants, and the new GenAI/LLM guardrail content are where people fail. |

**Readiness rule:** book the exam only after scoring ≥ 80% on an *official* Skill Builder practice exam, not a third-party one.

---

## 5. Podcast roadmap

As of 16 Aug 2026 every one of the three exams has **at least an hour** of published
audio. The target was an hour each, not full domain coverage — so the lists below mark
what is built and what is still open.

| Show | Episodes | Runtime | Coverage |
|---|---|---|---|
| `aws-ai-practitioner` — AIF-C01 | 9 | 66:38 | all 5 domains, plus prompting/parameters and evaluation |
| `aws-solutions-architect` — SAA-C03 | 6 | 69:41 | all 4 domains have an episode |
| `aws-security-specialty` — SCS-C03 | 6 | 70:04 | 5 of 6 domains, ~86% of the paper |

The `cert-prep` template encodes the instinct all of these run on: *"Certification exams
test discrimination, not recall… every concept must land as 'use X when Y, not Z because
W'."* AIF-C01 stays single-narrator on `cert-prep`; the two newer shows use
`cert-prep-2voice`, where a competent sceptic argues for the exam-wrong answer.

**Show `aws-solutions-architect` — "AWS Solutions Architect — SAA-C03"**

1. ✅ The Exam Map — 65 questions, 50 scored, 720 to pass, where the marks live
2. ✅ Domain 1a: Secure Architectures — IAM, identity federation, least privilege *(30% domain, split in two)*
3. ✅ Domain 1b: Secure Architectures — VPC design, endpoints, encryption at rest and in transit
4. ✅ Domain 2: Resilient Architectures — RPO/RTO, the four DR strategies, Multi-AZ vs read replicas, and decoupling *(built as one episode, not the two originally planned)*
5. ✅ Domain 3: High-Performing — compute, storage and database selection, and the four places a cache can live
6. ✅ Domain 4: Cost-Optimized — purchase models, storage classes, the transfer charges
7. ⬜ Service Discriminators I — storage and database look-alikes (EBS vs EFS vs FSx vs S3; RDS vs Aurora vs DynamoDB)
8. ⬜ Service Discriminators II — networking and integration look-alikes (ALB vs NLB vs API Gateway; SQS vs Kinesis vs MSK)
9. ⬜ The Well-Architected Framework as an answer-picking tool

**Show `aws-security-specialty` — "AWS Security Specialty — SCS-C03"**

1. ✅ The Exam Map — 750 to pass, ordering and matching questions, and what C03 changed
2. ✅ Domain 4: IAM (20%, biggest) — policy evaluation across all five policy types, plus RCPs
3. ✅ Domain 1: Detection — record/analyse/aggregate, and which service would have seen *this*
4. ✅ Domain 2: Incident Response — isolate before terminate, and revoking sessions a dead key already issued
5. ✅ Domain 5: Data Protection — KMS key policies, grants, envelope encryption, imported key material
6. ✅ Domain 3: Infrastructure Security — the edge inward, inter-node encryption, **and the GenAI guardrail content nobody else has made**
7. ⬜ Domain 6: Foundations & Governance — Organizations, SCPs, Control Tower, audit response *(the remaining 14%)*
8. ⬜ Domain 3b / 5b split — deeper network controls, and secrets, certificates and masking on their own

**Show `aws-ai-practitioner` — "AWS AI Practitioner — AIF-C01"** — 5 domain episodes, Exam
Map and Service Discriminators, plus two added on 16 Aug: prompting and inference
parameters with the three prompt attacks, and evaluation metrics with model selection.

### Sequencing suggestion
Study order is AIF → SAA → SCS, and the audio now supports all three. The one gap worth
closing before sitting SCS is Domain 6, governance — everything else is covered.
Ship remaining episodes one per study session so the podcast tracks the studying rather
than lagging it.

---

## 6. Sources

**Primary (AWS official)**
- SAA-C03 exam guide — https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html
- AIF-C01 exam guide — https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01.html
- SCS-C03 exam guide — https://docs.aws.amazon.com/aws-certification/latest/security-specialty-03/security-specialty-03.html
- SCS-C02 → SCS-C03 comparison appendix — https://docs.aws.amazon.com/aws-certification/latest/security-specialty-03/security-specialty-03-appendix-b.html
- AWS certification prep resources & Skill Builder pricing — https://aws.amazon.com/certification/certification-prep/
- Certification benefits (50% voucher) — https://aws.amazon.com/certification/benefits/
- Recertification rules — https://aws.amazon.com/certification/recertification/
- Coming soon / upcoming exam changes — https://aws.amazon.com/certification/coming-soon/
- AI portfolio expansion + Security update announcement — https://aws.amazon.com/blogs/training-and-certification/big-news-aws-expands-ai-certification-portfolio-and-updates-security-certification/

**Secondary (community / commercial — treat as opinion)**
- Tutorials Dojo, "What's New in SCS-C03" — https://tutorialsdojo.com/whats-new-in-aws-certified-security-specialty-scs-c03-exam-in-2025-2026/
- Tutorials Dojo practice exams — https://portal.tutorialsdojo.com/
- Stephane Maarek SAA-C03 — https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/
- Stephane Maarek AIF-C01 — https://www.udemy.com/course/aws-ai-practitioner-certified/
- Adrian Cantrill Security Specialty — https://learn.cantrill.io/p/aws-certified-security-specialty
- r/AWSCertifications vouchers & discounts wiki — https://awscertifications.github.io/AWSCertificationsWiki/vouchers-discounts/

**Adjacent, optional**
- AWS Certified Generative AI Developer – Professional (AIP-C01), GA March 2026, $300 — the natural follow-on to AIF-C01 — https://aws.amazon.com/certification/certified-generative-ai-developer-professional/
