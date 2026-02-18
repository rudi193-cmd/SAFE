SEED_PACKET 2026-02-17 (session 2)

MODELS ON HF: Sean(hf.co/Rudi193/sean-campbell, 5.4GB f16), Jane(hf.co/Rudi193/Jane, 2GB Q4), Kart(hf.co/Rudi193/Kart, 4.7GB Q4). All CC BY-NC 4.0.

SHIPPED THIS SESSION:
- user_registration.py (Willow/core) - user onboarding orchestrator
- aios-minimal DEPRECATED (bd29014)
- rag_search.py (Willow/skills) - RAG query skill, use this first
- journal_engine.py (Willow/core) - JSONL session engine
- sean_chat.py (Willow/agents) - ChatML format, 30% memory injection, fleet fallback
- setup_oracle_arm.sh + provision_oracle.py - OCI ARM provisioning
- upload_to_hf.py - HF upload script
- task_cache.py (~/.local/bin/scripts) - dedup task notifications silently
- JOURNAL_APP_SPEC.md - journal=training pipeline, 96% rule, Books of Life connection
- JOURNAL_APP_SPEC.md updated - 216 atoms->Part1, 64->Part2, 13->Part3->voice model

PENDING: OCI ARM still provisioning (oracle_create_arm.py running). Kaggle public re-run in progress. Q4 GGUF for Sean not yet downloaded locally.

SEAN MODEL: Llama-3.2-3B, ChatML format, im_start/im_end stop tokens, 30% memory injection, 23 domains, loss 1.04.

NEXT: atom_extractor.py (journal->knowledge.db), relationship_tracker.py, Willow fine-tune pipeline, Journal UI.

KEY: python=C:/Python314, rag_search skill exists, task_cache.py=silent dedup, fleet healthy (Ollama GLM-5).

DeltaSigma=42
