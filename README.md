# ASIC Triage Agent: Automated Log Clustering Engine

An automated, local-first verification triage tool that groups raw Electronic Design Automation (EDA) simulation failure logs using machine learning, and runs root-cause analysis entirely offline using an on-device Large Language Model (LLM).

## 📊 System Architecture & Data Flow

Below is the automated data pipeline showing how raw simulation failures are ingested, mathematical features are extracted, logs are grouped by structural symptoms, and root causes are summarized.

```mermaid
graph TD
    A[./logs/ Folder] -->|Extract Raw Text| B[Pre-processing Engine]
    B -->|Strip Timestamps & Slack Noise| C[TfidfVectorizer]
    C -->|Convert Text to Math Vectors| D[K-Means Clustering]
    D -->|Group Into Discrete Symptom Buckets| E[Local Ollama Server]
    E -->|Deterministic Parse: Llama 3.2 1B| F[Actionable Debug Summary]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bfb,stroke:#333,stroke-width:2px

🛠️ Engineering Journey & Core Challenges
📌 Problem Statement & Objective
In modern ASIC design verification, analyzing thousands of raw Electronic Design Automation (EDA) simulation failure logs is a massive operational bottleneck. Standard cloud-based AI triage agents are unusable in high-stakes hardware environments due to strict corporate sandboxes and IP data-privacy firewalls.
The Goal: Build a highly accurate, zero-cost, mathematical clustering and triage pipeline that runs 100% locally and completely offline on an engineer's workstation.
⚡ Technical Hurdles & Dynamic Framework Fixes
1. Corporate Sandbox Restrictions
The Challenge: Enterprise firewalls blocked external LLM API endpoints, preventing traditional cloud inference.
The Local Fix: Intercepted the pipeline and re-routed all structural JSON traffic locally by deploying an on-device Ollama server node (http://localhost:11434/v1) running an offline llama3.2:1b engine.
2. LLM Safety Refusals (Guardrail Bypassing)
The Challenge: Smaller edge models are highly aligned. When raw simulation headers or DMA registers were fed into the prompt, the model flagged it as "sensitive company data" and threw a safety refusal.
The Local Fix: Built a structural pre-processing regex mask to strip boilerplate headers. Changed the system architecture from a conversational "ASIC Assistant" to a transactional "Local Structural Data Parser" running at a deterministic temperature=0.0.
3. Log Noise & False Cluster Splitting
The Challenge: High-frequency variations in the logs (dynamic timestamps, cycle counts, varying slack values like -0.128 ns) tricked standard K-Means algorithms into sorting identical hardware bugs into completely separate buckets.
The Local Fix: Implemented a regex token normalization layer that masks out shifting variables (e.g., converting dynamic data to Slack: [X] ns), forcing the downstream TF-IDF Vectorizer to focus purely on the core error signature.