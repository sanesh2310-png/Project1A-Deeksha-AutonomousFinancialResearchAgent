# Optimization Log

## Optimization 1: Failure-injection timing (fixed a bug found during Day 12 stress testing)
**Before:** `_execute_tool()` re-rolled the injected-failure coin flip on
every retry attempt inside `call_with_retry()`. At a 50% per-attempt
failure rate and 5 retry attempts, the probability all 5 attempts failed
was only 0.5^5 ~= 3%, so Challenge 8's "simulate 50% failure rate" almost
never actually triggered a visible fallback -- retries silently absorbed
it. Tool efficiency and error-recovery metrics looked identical to a
zero-failure run, which is not a meaningful stress test.

**After:** the failure decision is made once per tool invocation, before
the retry loop, so a "down" tool stays down across all retry attempts
(simulating a genuinely unavailable service rather than a flaky one).

**Result:** Challenge 8 now logs real fallback substitutions and circuit
breaker activity (12 degradation notes across a single run in the bundled
example), and the stress test report's resilience ratio reflects an
actually-degraded run instead of a no-op.

## Optimization 2: Query-type classification ordering
**Before:** `_TYPE_KEYWORDS` checked generic single-word triggers (e.g.
`"risk"`) before more specific multi-word phrases. Challenge 7's query
("...what themes emerge across the technology sector? Identify
cross-cutting **risks** and opportunities.") was misclassified as
`risk_assessment` instead of `sector_memory`, because it happens to
mention "risks" in passing.

**After:** reordered the keyword table so specific phrases
(`"you've already researched"`, `"apparent contradiction"`,
`"complete investment research report"`) are checked before generic
single-word fallbacks.

**Result:** Challenge 7 now correctly triggers the `sector_memory` plan
(`vector_db_search` first, checking prior research) instead of a generic
risk-assessment tool sequence -- confirmed via the trace in
`docs/trace_gallery.md`.

## Optimization 3: Company-name-to-ticker resolution
**Before:** `query_analyzer._extract_tickers()` only matched bare
all-caps ticker symbols via regex, so prose queries like "Microsoft
Corporation" or "Compare ... Amazon (AWS), Microsoft (Azure), and Google
(GCP)" resolved to zero or wrong tickers (matching "AWS"/"GCP" as if they
were stock tickers).

**After:** added a company-name -> ticker lookup checked alongside the
regex, and excluded known product/brand acronyms (AWS, GCP, ECM) from
the ticker regex's positive matches.

**Result:** Challenge 4 now correctly researches MSFT, AMZN, and GOOGL
(three real companies) instead of misfiring on "AWS" as a ticker symbol.
