"""
Configuration module for the Autonomous Code Refactoring Agent.

Handles model settings, Ollama connection parameters, GPU detection,
and retry limits. All values can be overridden via environment variables.
"""

import os
import subprocess
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GPU Detection
# ---------------------------------------------------------------------------

def detect_gpu() -> bool:
    """
    Check for NVIDIA GPU availability by calling nvidia-smi.
    Returns True if an NVIDIA GPU is detected, False otherwise.
    """
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            logger.info("✅ NVIDIA GPU detected — Ollama will use GPU acceleration")
            return True
    except FileNotFoundError:
        pass  # nvidia-smi not installed
    except subprocess.TimeoutExpired:
        pass  # nvidia-smi hung

    logger.info("ℹ️  No NVIDIA GPU detected — Ollama will run on CPU only")
    return False


GPU_AVAILABLE: bool = detect_gpu()

# ---------------------------------------------------------------------------
# Model & Ollama Settings
# ---------------------------------------------------------------------------

MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-r1:7b")
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0"))
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# num_gpu=-1 offloads all layers to GPU; num_gpu=0 forces CPU-only
NUM_GPU: int = -1 if GPU_AVAILABLE else 0

# ---------------------------------------------------------------------------
# Agent Settings
# ---------------------------------------------------------------------------

MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
PYTEST_TIMEOUT: int = int(os.getenv("PYTEST_TIMEOUT", "30"))
