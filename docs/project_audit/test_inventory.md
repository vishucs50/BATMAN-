# Test Inventory

## Existing Tests
- **Unit Tests**:
  - `tests/unit/test_phase_one.py`: Tests HTN decomposition, COA generation pipeline, Threat network, Graph seeding.
  - `tests/unit/test_phase_two.py`: Comprehensive Phase 2 tests (Physics, Terrain, Simulation Events).
- **Integration Tests**:
  - `scripts/test_full_system.py`: End-to-end integration test across services.
  - `scripts/test_ai_pipeline.py`: Exercises the AI pipeline.
  - `scripts/test_phase1.py`, `scripts/test_phase2.py`, `scripts/test_phase3.py`: Specific phase integration validations.

## Coverage
- Broad coverage of simulation logic (Mesa models, events, logging) and planning (HTN, Constraint).

## Missing Tests
- **Frontend Tests**: No significant frontend test suite (e.g., Jest/Cypress) found.
- **API Contract Tests**: Explicit OpenAPI validation tests are minimal.
- **Load / Stress Tests**: Not currently present.
