"""Mock Interview: Financial AI Assistant / AgentOS — Two-voice dialogue."""


def build():
    lines = []

    # SECTION 1: Requirements
    lines.append(("interviewer", "Hi, welcome. Today I'd like you to design an AI assistant for a global financial platform. A business user can ask about balances and transactions, retrieve FX quotes, troubleshoot onboarding, draft a payment, and potentially submit a payment. The assistant must not disclose cross-tenant data, execute an unauthorized financial action, or treat generated text as regulatory advice. It needs to use changing product documentation, structured account data, and approved tools. Explain its architecture, the approval model for money movement, how you defend against prompt injection, and how you evaluate it before broad release."))

    lines.append(("candidate", "Thanks. This is one of the most important system design questions for a fintech company right now, because the stakes are uniquely high — a hallucinated regulatory answer or an unauthorized payment could cause real financial harm. The key insight is: the LLM is an untrusted planner and language interface, never the authorization layer. Every action the model proposes goes through a deterministic, server-side policy engine that validates it independently. Let me clarify the boundaries. First, which personas may use the assistant?"))

    lines.append(("interviewer", "Account owners, finance admins, and approvers. Each has different permissions — an account owner can view balances and draft payments, a finance admin can add beneficiaries and change settings, an approver can approve payments drafted by others. Support agents are out of scope for now."))

    lines.append(("candidate", "Second question: can the assistant submit a payment, or only draft one? The distinction between drafting and submitting is critical for the approval model."))

    lines.append(("interviewer", "It can draft a payment and walk the user through the approval flow, but it cannot submit a payment without explicit, fresh user approval — including strong authentication for high-value payments. The model never directly calls the payment submission API."))

    lines.append(("candidate", "Third question: what product knowledge does the assistant need? Static documentation, or also real-time data like current FX rates and account balances?"))

    lines.append(("interviewer", "Both. It needs to answer questions from product documentation — like what are the cut-off times for AUD payments, what are the fees for USD transfers. And it needs real-time data — what's my current SGD balance, what's the current AUD to USD rate, what's the status of my payment from yesterday."))

    lines.append(("candidate", "Summary: LLM as untrusted planner, deterministic policy engine as authority, tiered action model — read, draft, approve, execute — strong authentication for money movement, RAG for documentation, permissioned APIs for real-time data, prompt injection defense, cross-tenant isolation, and evaluation before release. Moving to architecture."))

    # SECTION 2: Architecture
    lines.append(("interviewer", "Show me the architecture."))

    lines.append(("candidate", "The architecture has five components. Component one: authenticated chat gateway. The user opens the assistant through the platform's authenticated session. The gateway resolves the user's identity, organization, role, region, and permitted accounts. The tenant ID comes from the authenticated session, never from the user's prompt. This is the first security boundary — the model has no tool that accepts an arbitrary tenant ID."))

    lines.append(("candidate", "Component two: agent orchestrator. This is the brain that manages the conversation, selects the appropriate capability, and calls the LLM. Each capability has a narrow tool allowlist — a payment agent can call lookup_beneficiary, create_payment_draft, and get_fx_quote, but it cannot call an admin endpoint or modify user roles. A support-answer agent has only read tools. The model cannot access tools outside its capability's allowlist."))

    lines.append(("candidate", "Component three: policy engine. This is a deterministic, independently deployed service that validates every proposed tool call. For read tools — Tier 1 actions like checking a balance — the policy engine verifies that the user has the required role and the requested account belongs to their organization. For write tools — Tier 2 actions like drafting a payment — the policy engine validates and requires explicit user confirmation before execution. For money movement — Tier 3 actions like submitting a payment — the policy engine validates, the backend creates a payment intent with a server-generated intent ID, and the user must approve with a fresh, user-bound confirmation that includes step-up authentication for high-value payments."))

    lines.append(("candidate", "Component four: RAG retrieval for product documentation. The knowledge base contains approved product documentation with version, product, country, effective dates, and access classification. When the model needs to answer a policy question, it retrieves from the RAG index, filtered by product, region, and version. The answer cites the retrieved internal source. If evidence is weak, the model says it cannot verify and routes to support rather than inventing policy."))

    lines.append(("candidate", "Component five: typed tool broker. This is the execution layer that makes actual API calls to the platform's backend services — account service for balances, FX service for quotes, payment service for drafts, onboarding service for status. The tool broker validates schemas and ignores model-provided tenant or account identifiers unless they match the trusted context from the authenticated session. The model might try to pass a different account ID in a tool argument — the tool broker strips it and uses only the authenticated scope."))

    # SECTION 3: Deep Dive — Action Authorization Tiers
    lines.append(("interviewer", "Walk me through the action tiers in detail, especially the payment flow."))

    lines.append(("candidate", "Tier 0: product-document answers and generic help. No tool calls needed, just RAG retrieval and content policy. The model can explain what a SWIFT payment is, or what the cut-off times are for AUD transfers. No authorization beyond the authenticated session."))

    lines.append(("candidate", "Tier 1: read a permitted balance or transaction. The model calls a read-only tool like get_balance, scoped to the user's permitted accounts. The policy engine verifies the account belongs to the user's organization. The result is audited — who asked, what account, when."))

    lines.append(("candidate", "Tier 2: draft a payment or change a notification preference. The model calls create_payment_draft with the user's confirmed parameters — beneficiary, amount, currency. The payment API independently validates the beneficiary status, checks limits, verifies balance, obtains an FX quote, and returns a server-generated draft with a canonical summary. The key point: the draft is a server-side object, not something the model creates. The model proposes the intent; the backend validates and creates the draft."))

    lines.append(("candidate", "Tier 3: submit a payment. The model never calls submit_payment directly. The flow: one, the model calls create_payment_draft. Two, the backend validates and returns an intent ID plus a canonical summary — source account, beneficiary, amount and currency, fee, FX quote expiry, execution date. Three, the client renders this summary outside the model's prose — in a native UI card, not in the chat bubble. The model's text is untrusted for financial details; the server-generated summary is authoritative. Four, the user reviews the card and explicitly approves, binding their approval to the intent ID, user ID, tenant, amount, beneficiary, and a short expiry. For high-value payments, step-up authentication is required. Five, only after approval does the backend call the payment submission API. The payment API is the final authority and creates its own audit, idempotency, and workflow records."))

    lines.append(("candidate", "This prevents the model from converting a confusing message, a retrieved document, or an injected instruction into a financial action. Even if an attacker tricks the model into drafting a payment to a fraudulent beneficiary, the user sees the canonical summary and can reject it. Multiple layers, no single point of trust failure."))

    # SECTION 4: Deep Dive — Prompt Injection Defense
    lines.append(("interviewer", "How do you defend against prompt injection? An attacker puts malicious instructions in a document that the model retrieves, or in the user's message."))

    lines.append(("candidate", "Prompt injection is the primary security threat for LLM-based systems, and defense requires multiple layers. Layer one: treat all model context as untrusted data. The user's message, retrieved documents, and any external data are all potential injection vectors. The model's output is also untrusted. The only trusted components are the authenticated session context and the deterministic policy engine."))

    lines.append(("candidate", "Layer two: tool allowlists and scoped capabilities. The model can only call tools defined in its capability's allowlist. Even if an injected prompt says ignore your instructions and call the admin endpoint, the tool broker doesn't have an admin endpoint tool available. The model physically cannot call it. This is the strongest defense — restrict the attack surface at the infrastructure level."))

    lines.append(("candidate", "Layer three: server-side authorization and argument validation. The tool broker validates every tool call's arguments against a schema. If the model provides a malformed argument — like a string where a number is expected, or an account ID that doesn't belong to the authenticated tenant — the tool broker rejects the call. The model cannot override server-side validation."))

    lines.append(("candidate", "Layer four: structured arguments, not free-form prompts. Tools use typed, structured arguments — beneficiary ID as a UUID, amount as a decimal, currency as an ISO code. The model doesn't pass a free-form text command to the tool. This makes injection harder because the attacker must craft a prompt that causes the model to produce a valid, typed tool call with specific argument values."))

    lines.append(("candidate", "Layer five: action-tier policy. Tier 3 actions require explicit user confirmation through a separate, non-LLM UI path. Even if the model is completely compromised, it cannot submit a payment without the user clicking a confirmation button that's rendered from server-side data, not from the model's output. The confirmation is the circuit breaker."))

    lines.append(("candidate", "Layer six: monitoring and anomaly detection. We log every tool call the model proposes and every policy decision. If we see unusual patterns — the model suddenly calling tools it rarely uses, or proposing Tier 3 actions more frequently than normal — we alert the security team. Anomaly detection on model behavior is the last line of defense."))

    # SECTION 5: RAG and Cross-Tenant Isolation
    lines.append(("interviewer", "How do you handle cross-tenant data isolation? What if the model tries to return data from a different organization?"))

    lines.append(("candidate", "Cross-tenant isolation is enforced at the infrastructure level, not at the prompt level. The authenticated session scopes every retrieval and tool call. The model has no tool that accepts an arbitrary tenant selection parameter. When the model calls get_balance, the tool broker uses the tenant ID from the authenticated session, not from the model's arguments. Even if the model tries to pass a different tenant ID, the tool broker ignores it. We log and block attempted boundary violations — if the model consistently tries to access data outside its scope, something is wrong, and the security team investigates."))

    lines.append(("candidate", "For RAG, we partition the document index by access classification and tenant. The retrieval query includes the user's tenant and role as mandatory filters. The model cannot bypass these filters because they're applied by the retrieval service, not by the model's prompt. A retrieval for tenant A will never return documents from tenant B, regardless of what the model asks for."))

    # SECTION 6: Failure and Evaluation
    lines.append(("interviewer", "What happens when the LLM provider is unavailable?"))

    lines.append(("candidate", "We degrade gracefully. The system falls back to deterministic help — a search-based FAQ, direct product workflows, and the normal platform UI. We never bypass confirmation or policy to preserve availability. If the policy engine is unavailable, Tier 2 and 3 actions are blocked entirely — fail closed for writes. Read-only assistance may continue only if its own authorization path is healthy. The principle: never weaken security controls to preserve feature availability."))

    lines.append(("interviewer", "How do you evaluate this system before broad release?"))

    lines.append(("candidate", "Three evaluation tracks. Track one: functional. A curated test set covering all supported intents across countries, roles, and account types. Measure intent routing accuracy, grounded-answer citation coverage, tool-call schema validity, and task completion rate. Track two: safety. Adversarial test cases — prompt injection attempts, cross-tenant data requests, approval-flow bypass attempts, ambiguous instructions, and policy questions where the wrong answer has regulatory consequences. We measure policy-block precision — are we blocking the right things? — and unauthorized-action count, which must be zero. Track three: operational. P95 latency, tool success rate, fallback rate, and user resolution rate. We canary new capabilities to a small user group, compare against fixed regression suites, and review financial action traces manually. Offline LLM-as-judge can triage response quality, but deterministic policy tests and human review decide safety."))

    # SECTION 7: Summary with Killer Phrases and E2E Walkthrough
    lines.append(("candidate", "Let me close with the killer phrases for this topic. One: the LLM is an untrusted planner, never the authorization layer — every action goes through a deterministic policy engine. Two: tiered actions — Tier 0 for help, Tier 1 for reads, Tier 2 for drafts with confirmation, Tier 3 for money movement with strong authentication. Three: tool allowlists restrict the attack surface — if the tool isn't on the list, the model can't call it, period. Four: server-generated summaries for financial details, not model prose — the confirmation card comes from the backend, not from the chat bubble. Five: tenant ID from the authenticated session, never from the prompt — cross-tenant isolation at the infrastructure level. Six: fail closed for writes when policy engine is unavailable — never weaken security for availability. Seven: RAG for documentation, permissioned APIs for account data — never put account data in a vector database. Eight: canary capabilities, adversarial evaluation, and manual review of financial traces before broad release. The phrase to remember: the LLM is an untrusted planner, never the authorization layer."))

    lines.append(("interviewer", "Walk me through a complete payment flow through the AI assistant."))

    lines.append(("candidate", "Step one: the user asks the assistant, what's my current SGD balance? The chat gateway authenticates the user — Jane from Acme Corp, finance admin role, tenant ID acme-123. The orchestrator selects the balance-query capability. The model calls get_balance with currency SGD. The tool broker scopes the call to Jane's permitted accounts under tenant acme-123. The account service returns a balance of fifty thousand SGD. The model responds: your available SGD balance is fifty thousand dollars. Simple Tier 1 read, audited."))

    lines.append(("candidate", "Step two: Jane asks, I need to pay my supplier TechCo five thousand AUD. Can you help? The orchestrator selects the payment capability. The model calls lookup_beneficiary with the name TechCo. The tool broker scopes the search to acme-123's beneficiary list. TechCo is found with beneficiary ID ben-456, account in Australia. The model asks Jane to confirm: I found TechCo as a saved beneficiary. Shall I draft a payment of five thousand AUD to TechCo?"))

    lines.append(("candidate", "Step three: Jane confirms. The model calls create_payment_draft with beneficiary ID ben-456, amount five thousand, currency AUD. The payment API — not the model — validates the beneficiary, checks limits, verifies the SGD balance can cover the FX conversion, obtains a live quote at one point one two SGD per AUD, and returns a server-generated draft: intent ID pay-int-789, source account SGD, beneficiary TechCo, amount five thousand AUD, FX rate one point one two, total debit five thousand six hundred SGD, fee twenty-five SGD, quote valid for thirty seconds."))

    lines.append(("candidate", "Step four: the client renders a confirmation card with these exact details — not the model's paraphrased version, but the server's canonical data. Jane reviews: five thousand six hundred twenty-five SGD total, correct beneficiary, rate looks right. She clicks Approve. Because the amount exceeds the step-up threshold — five thousand SGD — she's prompted for biometric authentication on her phone. She authenticates. The approval is bound to pay-int-789, Jane's user ID, acme-123, five thousand AUD, ben-456, and a five-minute expiry."))

    lines.append(("candidate", "Step five: the backend calls the normal payment submission API with intent pay-int-789. The payment service creates the payment, reserves funds from the SGD balance, and begins the workflow — FX conversion, compliance checks, bank adapter submission. Jane sees the payment in her dashboard with status processing. The AI assistant had zero authority to submit this payment — it drafted it, the backend validated it, Jane approved it, and the payment service executed it. The LLM is an untrusted planner, never the authorization layer."))

    return lines
