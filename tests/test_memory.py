import os
import tempfile

from memory.vector_store import VectorStore
from memory.episodic import EpisodicMemory


def test_vector_store_store_and_search_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "vs.json")
        vs = VectorStore(path=path)
        vs.store("Tesla faces supply chain risk in battery production.", {"ticker": "TSLA", "source_type": "sec_filing"})
        vs.store("Completely unrelated content about cooking recipes.", {"ticker": "N/A", "source_type": "news"})
        result = vs.search("Tesla supply chain battery", top_k=5)
        assert result["hits"], "expected at least one hit"
        assert result["hits"][0]["ticker"] == "TSLA"


def test_vector_store_persists_across_instances():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "vs.json")
        vs1 = VectorStore(path=path)
        vs1.store("Persistent content about Microsoft cloud growth.", {"ticker": "MSFT", "source_type": "analysis"})
        vs2 = VectorStore(path=path)
        assert vs2.count() == 1


def test_vector_store_filter_by_metadata():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "vs.json")
        vs = VectorStore(path=path)
        vs.store("Apple content", {"ticker": "AAPL", "source_type": "analysis"})
        vs.store("Microsoft content", {"ticker": "MSFT", "source_type": "analysis"})
        result = vs.search("content", top_k=5, filter={"ticker": "AAPL"})
        assert all(h["ticker"] == "AAPL" for h in result["hits"])


def test_episodic_memory_suggests_tool_order_from_success_history():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ep.json")
        ep = EpisodicMemory(path=path)
        ep.record("earnings_analysis", ["financial_data_api", "earnings_transcript", "web_search"], True, [])
        ep.record("earnings_analysis", ["financial_data_api", "earnings_transcript", "web_search"], True, [])
        order = ep.suggest_tool_order("earnings_analysis", ["web_search", "earnings_transcript", "financial_data_api"])
        assert order[0] == "financial_data_api"
