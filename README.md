# Autonomous Code Refactoring Agent 🤖

A fully local, agentic AI system that **plans**, **executes**, and **verifies** Python code refactoring — powered by a self-healing loop that runs tests and auto-repairs failures. Zero data egress. Runs on consumer hardware.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/LangGraph-Agent_Framework-2B6CB0?style=for-the-badge" alt="LangGraph">
  <img src="https://img.shields.io/badge/Ollama-Local_LLM-000000?style=for-the-badge" alt="Ollama">
  <img src="https://img.shields.io/badge/DeepSeek--R1-Reasoning_Model-FF6B35?style=for-the-badge" alt="DeepSeek-R1">
  <img src="https://img.shields.io/badge/GPU-Accelerated-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="GPU">
</p>

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔒 **Zero Data Egress** | Everything runs locally through Ollama — no code leaves your machine |
| 🧠 **Self-Verifying Loop** | The agent doesn't trust its own output — it proves correctness via pytest |
| 🔧 **Self-Healing Repair** | Failed refactorings are automatically debugged and retried (up to 3×) |
| 🛡️ **AST Safety Gate** | All generated code is parsed with `ast.parse()` before touching disk |
| 🚀 **GPU Acceleration** | Auto-detects NVIDIA GPUs; graceful CPU fallback on other machines |
| 📊 **Built-in Benchmarking** | 10 sample files, 173 tests, and a full metrics suite for measuring quality |

---

## 🏗️ Architecture

```
User Input (Python file)
        │
        ▼
┌─────────────────┐
│  Planner Node   │  ← DeepSeek-R1 (reasoning model)
│  (LangGraph)    │    Analyzes code smells, creates refactoring plan
└────────┬────────┘
         │  refactoring_plan
         ▼
┌─────────────────┐
│  Executor Node  │  ← DeepSeek-R1 + AST validation
│  (LangGraph)    │    Applies the plan, validates syntax before accepting
└────────┬────────┘
         │  refactored_code
         ▼
┌─────────────────┐
│  Verifier Node  │  ← PyTest subprocess
│  (LangGraph)    │    Swaps code, runs tests, restores original
└────────┬────────┘
         │
    ┌────┴────┐
  PASS      FAIL
    │          │
    ▼          ▼
  Output   Self-Repair Node  ← DeepSeek-R1
  (.bak     Reads error logs,
  backup)   patches the code
                 │
                 └──► back to Verifier (max 3 retries)
```

The pipeline is orchestrated as a **LangGraph state machine** with conditional edges. The Verifier routes to `END` on success or max retries, and to `Repair` on failure.

---

## 📦 Tech Stack

| Component | Purpose |
|-----------|---------|
| **[LangGraph](https://github.com/langchain-ai/langgraph)** | Agent state machine and node orchestration |
| **[Ollama](https://ollama.com)** | Local model server — zero data egress |
| **[DeepSeek-R1:7b](https://ollama.com/library/deepseek-r1)** | 4-bit quantized reasoning model (Q4_K_M) |
| **[PyTest](https://docs.pytest.org)** | Test runner for the verification loop |
| **Python AST** | Safe code parsing and validation |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.com/download)** installed and running
- **DeepSeek-R1:7b** model pulled:

```bash
ollama pull deepseek-r1:7b
```

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/autonomous-refactoring-agent.git
cd autonomous-refactoring-agent
pip install -r requirements.txt
```

### Run It

```bash
# Refactor a file (writes changes + creates .bak backup)
python -m src.cli path/to/your_code.py

# Dry run — see the plan without writing changes
python -m src.cli path/to/your_code.py --dry-run

# Verbose logging
python -m src.cli path/to/your_code.py -v

# Custom retry limit
python -m src.cli path/to/your_code.py --max-retries 5
```

### Try the Included Sample

```bash
python -m src.cli samples/messy_utils.py --dry-run
```

---

## 🔄 How the Self-Healing Loop Works

```
1. PLAN    →  LLM analyzes code smells and outputs a numbered action plan
2. EXECUTE →  LLM applies the plan; output is AST-validated before acceptance
3. VERIFY  →  Original file is backed up, refactored code is swapped in,
              pytest runs against the test suite
4. PASS?   →  ✅ Write refactored code to disk (backup preserved)
   FAIL?   →  🔧 Self-Repair reads test errors, patches the code
5. RETRY   →  Steps 3–4 repeat up to 3 times before the agent gives up
```

**Safety guarantees:**
- Original file is **always backed up** before any changes
- AST validation prevents **syntactically broken code** from ever being written
- If all retries fail, the **original file is preserved unchanged**

---

## 📊 Benchmark Suite

The project includes **10 deliberately messy Python files** (921 LOC, 69 functions) covering diverse code smells:

| # | Sample | Code Smells Targeted |
|---|--------|---------------------|
| 1 | `messy_utils.py` | Duplicated logic, vague names, bare excepts |
| 2 | `sample_02_strings.py` | String concat in loops, duplicated validation |
| 3 | `sample_03_data.py` | Deep nesting, bare excepts, god function |
| 4 | `sample_04_csv.py` | Manual string building, bubble sort |
| 5 | `sample_05_math.py` | Single-letter names, duplicated sort logic |
| 6 | `sample_06_cart.py` | Duplicated subtotal, OOP anti-patterns |
| 7 | `sample_07_auth.py` | Hardcoded values, duplicated validation |
| 8 | `sample_08_tasks.py` | `== True/False` comparisons, deep nesting |
| 9 | `sample_09_matrix.py` | Nested loops, no validation, no type hints |
| 10 | `sample_10_inventory.py` | God class, manual aggregation |

### Baseline Metrics (Pre-Refactoring)

| Metric | Value |
|--------|-------|
| Total Lines of Code | 921 |
| Total Functions | 69 |
| Avg Cyclomatic Complexity | 3.78 / function |
| Type Hint Coverage | 0.0% |
| Bare Except Clauses | 4 |
| `== None` Comparisons | 10 |
| String Concat in Loops | 61 |

### Run the Benchmark

```bash
# Baseline code quality metrics (no Ollama needed)
python benchmark.py --metrics-only

# Full pipeline benchmark on all 10 files
python benchmark.py

# Export detailed JSON report
python benchmark.py --report results.json
```

### Metrics Measured

**Pipeline metrics:**
- Success rate — % of files where refactored code passes all tests
- Self-repair recovery rate — % of failures saved by the repair loop
- Retry distribution — avg retries per file
- Per-file latency — seconds through full pipeline

**Code quality delta (before → after):**
- Lines of code change
- Cyclomatic complexity reduction
- Type hint coverage improvement
- Anti-pattern elimination (bare excepts, `== None`, string concat)
- Docstring coverage gain

---

## 🧪 Testing

```bash
# Run all tests (195 total — no Ollama needed)
python -m pytest tests/ samples/ -v

# Agent unit tests only (22 tests, mocked LLM)
python -m pytest tests/ -v

# Sample code tests only (173 tests)
python -m pytest samples/ -v
```

| Test Suite | Tests | Requires Ollama |
|-----------|-------|----------------|
| AST validation & markdown stripping | 12 | ❌ |
| Graph routing & mocked LLM nodes | 10 | ❌ |
| 10× sample file tests | 173 | ❌ |
| **Total** | **195** | ❌ |

---

## ⚙️ Configuration

All settings have sensible defaults. Override via `.env` or environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `MODEL_NAME` | `deepseek-r1:7b` | Ollama model to use |
| `MAX_RETRIES` | `3` | Self-repair retry limit |
| `PYTEST_TIMEOUT` | `30` | Seconds before killing a test run |
| `TEMPERATURE` | `0` | LLM temperature (0 = deterministic) |

```bash
cp .env.example .env
# Edit .env as needed
```

### GPU Support

The agent **auto-detects NVIDIA GPUs** via `nvidia-smi` on startup:
- **GPU found** → All model layers offloaded to GPU (`num_gpu=-1`)
- **No GPU** → Runs on CPU only (`num_gpu=0`)

No configuration needed — it just works.

---

## 📁 Project Structure

```
autonomous-refactoring-agent/
├── .env.example                 # Environment variable template
├── .gitignore
├── README.md
├── benchmark.py                 # Benchmark runner with all metrics
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── config.py                # GPU detection, model settings, constants
│   ├── state.py                 # AgentState TypedDict
│   ├── llm.py                   # OllamaLLM wrapper + health check
│   ├── metrics.py               # Static code quality analyzer (AST-based)
│   ├── graph.py                 # LangGraph state machine wiring
│   ├── cli.py                   # CLI entry point (argparse)
│   └── nodes/
│       ├── __init__.py
│       ├── planner.py           # Analyzes code → refactoring plan
│       ├── executor.py          # Applies plan → AST-validated code
│       ├── verifier.py          # Runs pytest with backup/restore
│       └── repair.py            # Reads errors → patches code
│
├── samples/                     # 10 benchmark files + test suites
│   ├── messy_utils.py           # Sample 1: General utilities
│   ├── test_messy_utils.py
│   ├── sample_02_strings.py     # Sample 2: String manipulation
│   ├── ...                      # Samples 3–10
│   └── test_sample_10_inventory.py
│
└── tests/                       # Agent's own tests (mocked LLM)
    ├── test_ast_validation.py   # AST parsing + fence stripping
    └── test_graph.py            # Routing logic + node behavior
```

---

## 🗣️ Resume Talking Points

- **Zero data egress**: entire pipeline runs locally through Ollama — no code leaves the machine
- **Self-verifying agent**: doesn't trust its own output — proves correctness via automated tests
- **Self-healing repair loop**: reads test errors, patches code, and re-verifies (up to 3 retries)
- **AST safety gate**: all LLM-generated code is parsed before disk writes, preventing broken files
- **GPU-accelerated with fallback**: auto-detects NVIDIA hardware, degrades gracefully to CPU
- **Quantified results**: benchmarked across 10 files with 173 tests measuring success rate, complexity reduction, and type hint coverage

---

## 📄 License

This project is open source under the [MIT License](LICENSE).
