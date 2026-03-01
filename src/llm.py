"""
LLM wrapper for the Autonomous Code Refactoring Agent.

Initializes a single OllamaLLM instance configured with the model,
temperature, base URL, and GPU settings from config.py.
All nodes import `llm` from this module.
"""

import logging
import requests

from langchain_ollama import OllamaLLM

from .config import MODEL_NAME, TEMPERATURE, OLLAMA_BASE_URL, NUM_GPU, GPU_AVAILABLE

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LLM Instance
# ---------------------------------------------------------------------------

llm = OllamaLLM(
    model=MODEL_NAME,
    temperature=TEMPERATURE,
    base_url=OLLAMA_BASE_URL,
    num_gpu=NUM_GPU,
)


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

def check_ollama_connection() -> bool:
    """
    Verify that:
      1. The Ollama server is reachable.
      2. The required model is available.
      3. Log whether GPU or CPU mode is active.

    Returns True if everything is ready, False otherwise.
    """
    # 1. Check server is reachable
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
    except requests.ConnectionError:
        logger.error(
            f"❌ Cannot connect to Ollama at {OLLAMA_BASE_URL}. "
            "Is Ollama running?  Start it with: ollama serve"
        )
        return False
    except requests.RequestException as exc:
        logger.error(f"❌ Ollama health-check failed: {exc}")
        return False

    # 2. Check model is available
    available_models = [
        m.get("name", "") for m in resp.json().get("models", [])
    ]
    # Ollama returns names like "deepseek-r1:7b" — match on prefix
    model_found = any(MODEL_NAME in m for m in available_models)
    if not model_found:
        logger.error(
            f"❌ Model '{MODEL_NAME}' not found in Ollama. "
            f"Pull it with: ollama pull {MODEL_NAME}"
        )
        return False

    # 3. Log GPU / CPU mode
    if GPU_AVAILABLE:
        logger.info(f"🚀 GPU mode active — all layers offloaded (num_gpu={NUM_GPU})")
    else:
        logger.info(f"🖥️  CPU mode active (num_gpu={NUM_GPU})")

    logger.info(f"✅ Ollama connection OK — model '{MODEL_NAME}' ready")
    return True
