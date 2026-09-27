# ERROR_LOG.md
## Project 1A — Autonomous Financial Research Agent
### Deliberate Error Detection Exercise (Section A4, "Error Detection Exercise")

The project brief states it contains exactly 7 deliberate factual/logical errors across Parts A–E.
Below are the 7 errors identified, their location, and the reasoning behind each.

---

### Error 1 — Contradictory metric formula (AB-4 Memory Utilization)
**Location:** Section A5.2, Category 5: Agent Behaviour, metric AB-4

**The error:** The metric is defined as "the ratio of memory_hits to total external API calls,"
but the same bullet then adds: *"This metric is calculated as memory_hits multiplied by
total_api_calls."*

**Why it's wrong:** A ratio requires division (`memory_hits / total_api_calls`). Multiplying the
two values instead produces an unbounded number with no meaningful relationship to the stated
target (">= 0.3"), and contradicts the metric's own definition in the same sentence.

**Correct version:** `AB-4 = memory_hits / total_api_calls`

---

### Error 2 — Impossible chronology in stress-test disambiguation example
**Location:** Section A7.3, "Handling Ambiguous Queries"

**The error:** "Note: The first US bank stress tests under SCAP were conducted in 2007
following the Dodd-Frank Act."

**Why it's wrong:** Two factual problems stack here:
1. SCAP (Supervisory Capital Assessment Program) was conducted in **2009**, as the same
   paragraph correctly states one sentence earlier — not 2007.
2. The Dodd-Frank Act was signed into law in **2010** — it cannot have caused an event
   (SCAP) that the text places in 2007, three years before the law existed.

**Correct version:** SCAP was conducted in 2009, in response to the 2008 financial crisis,
and predates Dodd-Frank (2010) — SCAP was not created "following" Dodd-Frank.

---

### Error 3 — Fabricated, uncited industry statistic
**Location:** Case Study 3 (Alpha Research Labs), Section C3.2

**The error:** "Note: Industry average hallucination rates for unverified financial agents
are typically around 45-60%."

**Why it's wrong:** This figure is presented as established fact with no source, doesn't
correspond to any published benchmark literature on RAG/agent hallucination rates, and is
inconsistent with the case study's own numbers (the failed agent's 23% rate is presented as
notably *bad*, which wouldn't make sense if 45-60% were the industry average).

---

### Error 4 — Tool name mismatch between example and registry
**Location:** Section A1.3 (ReAct example) vs. Section A2.2 (Tool Registry table)

**The error:** The worked ReAct example calls `search_sec_filings(ticker='TSLA',
filing_type='10-K', year=2024)`, but the actual tool registry defines the tool as
**`sec_filing_search`** (Section A2.2 and confirmed again in the JSON schema example,
A2.4).

**Why it's wrong:** These are two different, incompatible function names. An agent
implementation built strictly from the registry would have no tool named
`search_sec_filings` and the example call would fail.

**Correct version:** `Action 1: sec_filing_search(ticker='TSLA', filing_type='10-K', year=2024)`

---

### Error 5 — Wrong regulatory filing form attributed to India
**Location:** Case Study 4, Section C4.2

**The error:** "Indian companies file annual returns using Form 20-F with the MCA (Ministry
of Corporate Affairs), similar to the 10-K filing in the US system."

**Why it's wrong:** Form 20-F is a **US SEC** form filed by foreign private issuers listing
on US exchanges — it has no connection to India's Ministry of Corporate Affairs. Indian
companies file their annual returns with the MCA using forms such as **AOC-4** (financial
statements) and **MGT-7** (annual return), not Form 20-F.

---

### Error 6 — Incorrect embedding dimensionality
**Location:** Section E2.2, "Recommended Embedding Models"

**The error:** "OpenAI text-embedding-3-large: 1024 dimensions, $0.13 per million tokens."

**Why it's wrong:** text-embedding-3-large's native dimensionality is **3072**, not 1024.
(The API does allow truncating output dimensions down via a `dimensions` parameter, but
1024 is not its default/native size, and presenting it as "the" dimension count is
incorrect — the pricing figure of $0.13/million tokens is correct.)

---

### Error 7 — Illogical source reliability ranking
**Location:** Section A6.2, "Source Reliability Hierarchy"

**The error:** The hierarchy ranks Tier 4 as "Social media posts and anonymous forum
discussions" and Tier 5 (the *least* reliable tier, since Tier 1 is highest) as "Major news
outlets (Reuters, Bloomberg News, Financial Times)."

**Why it's wrong:** This ranks professionally edited journalism as **less reliable than
anonymous, unverified social media posts** — backwards from any sensible reliability
ordering, and inconsistent with the document's own Case Studies 1 and 2, which emphasize
Bloomberg's and S&P Global's investment in professional journalism as a *reliability*
advantage.

**Correct version:** Major news outlets (Tier 4) should rank above social media / anonymous
forums (Tier 5), reflecting editorial oversight vs. crowd-sourced, unverified content.

---

## Summary Table

| # | Location | Type of Error |
|---|----------|---------------|
| 1 | Section A5.2 (AB-4) | Incorrect formula / internal contradiction |
| 2 | Section A7.3 | Factual + chronological error |
| 3 | Case Study 3 (C3.2) | Fabricated/unsupported statistic |
| 4 | Section A1.3 vs A2.2 | Naming inconsistency (would break implementation) |
| 5 | Case Study 4 (C4.2) | Wrong regulatory/API specification |
| 6 | Section E2.2 | Incorrect technical specification |
| 7 | Section A6.2 | Illogical/inverted ranking logic |
