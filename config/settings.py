"""
Central configuration for the Autonomous Research Agent (ARA-1).

All values can be overridden via environment variables (see .env.example).
Loaded once at import time via python-dotenv.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


# --- LLM configuration -----------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
# If neither key is configured, the agent automatically falls back to a
# deterministic SimulatedPlanner (see agent/simulated_planner.py) so the
# whole pipeline runs end-to-end without any external LLM access. This is
# also what the test suite exercises, so CI never needs live API keys.
USE_REAL_LLM = bool(ANTHROPIC_API_KEY or OPENAI_API_KEY)

# --- Agent loop control -----------------------------------------------------
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "12"))
MAX_TOOL_CALLS_PER_TASK = int(os.getenv("MAX_TOOL_CALLS_PER_TASK", "20"))

# --- Error handling ----------------------------------------------------------
RETRY_INITIAL_DELAY_SECONDS = float(os.getenv("RETRY_INITIAL_DELAY_SECONDS", "1.0"))
RETRY_MAX_ATTEMPTS = int(os.getenv("RETRY_MAX_ATTEMPTS", "5"))
RETRY_JITTER_MS = int(os.getenv("RETRY_JITTER_MS", "500"))
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "3"))
CIRCUIT_BREAKER_COOLDOWN_SECONDS = float(os.getenv("CIRCUIT_BREAKER_COOLDOWN_SECONDS", "10"))

# --- Memory ------------------------------------------------------------------
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./memory/.vector_store.json")
EPISODIC_STORE_PATH = os.getenv("EPISODIC_STORE_PATH", "./memory/.episodic_store.json")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "256"))
VECTOR_DB_TOP_K_DEFAULT = int(os.getenv("VECTOR_DB_TOP_K_DEFAULT", "5"))

# --- Synthesis -----------------------------------------------------------------
# Source reliability hierarchy (Tier 1 = most reliable).
# NOTE: this ordering intentionally fixes an error identified in the project
# brief (Section A6.2), which ranked "Major news outlets" *below* social
# media / anonymous forums. Professionally edited journalism belongs above
# unverified crowd-sourced content -- see ERROR_LOG.md, Error 7.
SOURCE_RELIABILITY_TIERS = {
    "sec_filing": 1,
    "financial_data_api": 2,
    "earnings_transcript": 3,
    "news_outlet": 4,
    "social_media": 5,
}
CONFLICT_THRESHOLD_PCT = float(os.getenv("CONFLICT_THRESHOLD_PCT", "5.0"))

# --- Networking / mock mode ----------------------------------------------------
# Real outbound calls to SEC EDGAR / financial data providers are attempted
# first; if they fail (no network access, no API key, timeout) each tool
# transparently falls back to a deterministic mock data generator so the
# pipeline still produces a complete, clearly-labeled result.
FORCE_MOCK_MODE = _bool("FORCE_MOCK_MODE", True)
HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "6"))

# --- Logging -------------------------------------------------------------------
LOG_DIR = os.getenv("LOG_DIR", "./results/_traces")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
