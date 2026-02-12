# ADR-017: Universal Agent - V2 & V3 Integration Roadmap

## Status
Proposed

## Context
Currently, `sdml` (Image/SD focused) and `snsw` (Speech/TTS focused) exist as separate entities with overlapping logic for Docker management, Mail-based orchestration, and UI. To achieve maximum efficiency and code reuse, we need to unify these into a single "Universal Agent" framework.

## Roadmap

### V2: The Multi-Modal Core (TTS + ML + SD)
**Goal**: Consolidate Image and Speech generation into a single unified workspace.
- **Unified Mail Engine**: Merge `sdml/Mail_Manager` and `snsw/src/mail-order-agent.py` into a single, robust Python module that can handle diverse task schemas (Image, Audio, Text).
- **Shared Worker Orchestrator**: A single `universal-agent.ps1` (evolving from `snsw-agent.ps1`) that can spawn containers for both SD and TTS tasks.
- **Unified WebView**: The `webview-manager.py` becomes the dashboard for all AI modalities, displaying both image galleries and audio players.
- **Common Code Extraction**:
    - `core/docker_utils.py`: Shared logic for image/container management.
    - `core/mail_protocol.py`: Standardized JSON schema for inter-agent communication.
    - `core/ui_components.py`: Shared Flask/HTML templates.

### V3: Vision & Perception (VLM Integration)
**Goal**: Enable the Agent to "see" and "critique" its own output.
- **VLM Integration**: Incorporate Vision Language Models (e.g., Moondream, LLaVA, or specialized local VLMs) to analyze generated images and videos.
- **Feedback Loop**: The VLM acts as an internal reviewer. If an image doesn't match the prompt, it sends a "Correction Mail" back to the SD worker.
- **Metadata Generation**: Automatically generate captions, alt-text, and descriptions for audio-visual content.

## Architectural Benefits
- **Resource Efficiency**: Shared model caches and base Docker layers reduce disk and memory usage.
- **Simplified Maintenance**: One UI, one orchestration script, and one set of core libraries to update.
- **Generalization**: The Agent becomes task-agnostic. Adding a new modality (e.g., Music, 3D) just means adding a new Worker type, not rebuilding the whole system.

## Integration Plan
1. **Directory Merging**: Transition to a structure where `src/workers/` contains specialized AI logic and `src/core/` contains the universal engine.
2. **Protocol Standardization**: Finalize the "Agent Mail Protocol" to support multi-modal attachments.
3. **VSX Expansion**: Update the VS Code extension to support the new unified dashboard.

## Vision
The Universal Agent will act as a "General Purpose AI Concierge" that operates entirely locally, utilizing a swarm of specialized small models to fulfill complex creative requests.
