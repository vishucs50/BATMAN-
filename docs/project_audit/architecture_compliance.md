# Architecture Compliance

## Comparison against BATMAN_Architecture.md

### Missing Modules
- **Logistics & Resource Mgr Service**: Mentioned in orchestration layer, but largely absorbed by `wargame-svc` and doesn't exist as an independent microservice.
- **Situation Awareness Fusion**: Some sensor logic in `wargame-svc`, but no dedicated fusion service.

### Broken Integrations / Placeholder Implementations
- **GNN Reasoner (Knowledge Graph)**: Architecture lists PyTorch/GAT-based reasoning. Current implementation is a placeholder returning static mock responses.
- **Case-Based Reasoning (CBR)**: Architecture specifies FAISS vector store. Current implementation uses basic mock similarity.
- **Rule Engine (RETE)**: Architecture specifies a RETE network. Implementation is simplified and hardcoded.
- **Ant Colony Optimization (Constraint Solver)**: Currently implemented as a basic/simplified constraint solver rather than full ACO.
- **Explainability (XAI)**: Generates basic templates rather than deep source-traced semantic trees.

### Architecture Violations
- **Monolithic Frontend Slices**: Instead of subscribing to a centralized Message Bus (Kafka) via GraphQL/Websockets for all state changes, the frontend uses discrete REST polling/axios calls for most views.
- **Service Boundaries**: Logistics is tightly coupled into `wargame-svc` rather than standing alone.

### Dead Code
- No significant dead code found, but many modules (especially in `ai/` and `planning-svc/`) have `pass` or placeholder `TODO` blocks representing incomplete Phase 3 logic.
