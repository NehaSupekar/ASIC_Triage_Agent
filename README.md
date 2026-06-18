# 🤖 ASIC Triage Agent V2: Multi-Agent Automated Error Analysis Engine

An event-driven, local AI-powered engineering triage pipeline that monitors hardware simulation logs, groups them into semantic vector clusters using an embedding database, and deploys an asynchronous swarm of specialized LLM agents to perform structural Root Cause Analysis (RCA).

Built using **FastAPI**, **ChromaDB**, **Ollama (Llama 3.2 via Metal GPU acceleration)**, and **Streamlit**.

---

## 🏗️ Architectural Topology

The pipeline consists of three independent, highly decoupled stages running locally on-device:

1. **The Ingestion Gate (Watchdog & FastAPI):** An event-driven background file-system watcher monitors local directories. The moment a new simulator `.log` file is dropped, the event loop catches the file.
2. **The Vector Engine Guardrail (ChromaDB):** Log files are stripped of dynamic noise (such as absolute timestamps or fluctuating cycles) and converted into vector embeddings. If the log matches an existing failure signature's spatial coordinates, it shortcuts processing and auto-groups it to optimize compute. If it is a completely new signature, a new cluster category is generated.
3. **The Asynchronous Agent Swarm (Ollama):** A specialized multi-agent pipeline is initialized asynchronously over a native loopback network pipe (`httpx`):
   * **ASIC Static Timing Analysis (STA) Engineer:** Evaluates clock skews, domain transitions, and setup/hold window constraints.
   * **Principal RTL Design Engineer:** Scans for protocol deadlocks, hardware state-machine lockups, and interface buffer contentions.
   * **Lead Triage Architect (Orchestrator):** Synthesizes the domain reviews, eliminates technical contradictions, and caches a unified master Markdown report back into the vector database.

---

## 🚀 Local Installation & Setup

Follow these steps to run the pipeline locally on your machine.

### Prerequisites
* **Python:** Version 3.10 or higher
* **Ollama:** [Download Ollama for your OS](https://ollama.com/) (Fully optimized for Apple Silicon Metal acceleration)

### 1. Model Preparation
Open a terminal and download the local weights for the specialized agent model:
```bash
ollama run llama3.2:1b