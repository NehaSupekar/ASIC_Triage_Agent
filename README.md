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