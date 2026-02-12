# ADR-016: SNSW-AI V2 - Mail-Driven Agent/Worker Architecture

## Status
Proposed

## Context
V1 successfully established a CLI and simple WebView UI for orchestrating Docker-based AI tools (TTS, Image Gen). However, the interaction is still largely manual and rigid. The user wants a more flexible, conversational, and decentralized "V2" system.

## Goals
- **UX**: Conversational ordering via a "Mail" metaphor.
- **Privacy/Efficiency**: No external AI (OpenAI/Claude) for core tasks; use small local models.
- **Scalability**: Decentralized workers (Image, TTS, Logic) that can live in different containers/instances.
- **Simplicity**: No TypeScript; focus on Python and single-file HTML/JS for UIs.
- **Mobility**: Containers that can easily move across devices.
- **Learning**: Separate learning loop (Fine-tuning) to improve the system over time without affecting inference.

## Proposed Architecture

### 1. The Mail Agent (Orchestrator/Brain)
- **Role**: Parses user requests (Mails), decides which worker to call, and handles delivery.
- **Implementation**: A Python service with a lightweight LLM (e.g., Phi-3, TinyLlama) to parse intent.
- **Communication**: Monitors a `mail_inbox` (JSON files) and emits `task_orders` (JSON files).

### 2. The Workers (Execution/Hands)
- **Role**: Specialized tasks (TTS Worker, Image Worker, Video Worker).
- **Decentralization**: Each worker has its own HTTP endpoint or monitors its own queue folder.
- **Independence**: Can be built as separate Docker images or run in the same one.

### 3. The VSX/WebView Interface
- **Role**: The "Mail Client" where the user writes prompts and receives artifacts.
- **Tech Stack**: 
  - Backend: Flask/FastAPI (Python).
  - Frontend: Single HTML/JS/CSS file (No TS).
  - Integration: VS Code WebView (thin wrapper) or standalone browser.

### 4. The Learning Loop (Separate Pipeline)
- **Role**: Collects user feedback (e.g., "This image is bad", "This voice is good") and fine-tunes the local models.
- **Isolation**: Runs as a separate batch process to avoid resource contention with real-time generation.

### 5. Deployment & Mobility
- **Containerization**: Everything is Docker-native.
- **Portability**: Volume mounts for models/data allow the system to move from a high-end PC to a home server or mobile-accessible edge node easily.

## Key Principles
1. **Agent-Worker Split**: The brain (Agent) only knows *what* to do; the hands (Workers) know *how* to do it.
2. **Mail Metaphor**: Provides a natural time-based thread for orders and deliveries.
3. **No TS Policy**: Maintains a low barrier for entry and avoids build-step complexity in the UI.

## Next Steps
1. Prototype the "Mail Agent" using a small local LLM.
2. Define the JSON schema for "Inter-Agent Mail".
3. Implement a thin VS Code Extension (VSX) that points to the Flask WebView.
