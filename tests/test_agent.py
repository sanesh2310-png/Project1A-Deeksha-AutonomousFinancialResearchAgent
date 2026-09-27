import os
import tempfile

import config.settings as settings


def _fresh_agent(tmp_dir, **kwargs):
    from agent.core import ResearchAgent
    settings.VECTOR_STORE_PATH = os.path.join(tmp_dir, "vs.json")
    settings.EPISODIC_STORE_PATH = os.path.join(tmp_dir, "ep.json")
    return ResearchAgent(session_id="test-session", **kwargs)


def test_agent_produces_all_required_sections():
    from evaluation.metrics import REQUIRED_SECTIONS
    with tempfile.TemporaryDirectory() as d:
        agent = _fresh_agent(d)
        result = agent.run("Create a comprehensive profile of Microsoft Corporation.")
        for section in REQUIRED_SECTIONS:
            title = section.replace("_", " ").title()
            assert title.split()[0] in result["report_markdown"] or section in result["report_markdown"].lower().replace(" ", "_")


def test_agent_handles_ambiguous_query_with_disambiguation():
    with tempfile.TemporaryDirectory() as d:
        agent = _fresh_agent(d)
        result = agent.run("What's happening with the banks?")
        assert result["disambiguation"] is not None
        assert result["disambiguation"]["proxy_tickers"], "expected proxy tickers for ambiguous sector query"


def test_agent_gracefully_degrades_under_forced_failures():
    with tempfile.TemporaryDirectory() as d:
        agent = _fresh_agent(d, failure_injection_rate=1.0)  # force every primary tool to fail
        result = agent.run("Produce a complete investment research report on NVIDIA Corporation.")
        # Even with every primary tool failing, the pipeline must still
        # produce a complete report rather than crashing.
        assert result["report_markdown"]
        assert len(result["degradation_notes"]) > 0


def test_agent_stores_findings_in_long_term_memory():
    with tempfile.TemporaryDirectory() as d:
        agent = _fresh_agent(d)
        agent.run("Create a comprehensive profile of Microsoft Corporation.")
        assert agent.vector_store.count() >= 1


def test_agent_second_query_can_retrieve_first_from_memory():
    with tempfile.TemporaryDirectory() as d:
        agent = _fresh_agent(d)
        agent.run("Create a comprehensive profile of Microsoft Corporation.")
        result2 = agent.run("Based on the companies you've already researched, what themes emerge across the technology sector?")
        memory_calls = result2["gathered"].get("vector_db_search", [])
        assert memory_calls, "expected the second query to invoke vector_db_search"
