# Review response — two-source definite outcomes + deadlines never void an active dispute (Sep 14 follow-up)

Thank you for the follow-up. Both requested contract changes are in place, and the reproducible offline simulation now covers the complete lifecycle you asked us to verify.

## Your request (Sep 14, Pavel Kolosov)
1. A definite YES or NO result must require at least two independently binding-verified sources.
2. The final deadline must not void a market while its configured dispute process is still active.
3. Add source-level tests: one-source fallback, the initial dispute window, both dispute rounds, and finalization at their deadline boundaries.

## 1. Two independent binding-verified sources required for a definite outcome
Resolution runs the deterministic binding-excerpt check on every declared source, identically on every node. A definite YES/NO is only permitted when at least two sources — from at least two different domains — pass that check:

- contracts/prediction_market.py -> _resolve_now(): when `verified_count < 2 or domain_count < 2` the outcome is forced to UNRESOLVED and the market stays open/retryable.
- The comparative LLM step is never reached below the two-source threshold, so a single admissible source can never yield a definite result.

## 2. The final deadline can never void an active dispute
finalize() is the permissionless deadline exit, but it refuses to run while a dispute is live:

- contracts/prediction_market.py -> finalize(): computes `dispute_active` (status == "disputed", or an open dispute window with `now < dispute_deadline`) and asserts:
  "dispute process still active: finalize unlocks after the dispute window closes / dispute is resolved"
- void() likewise reverts during a dispute: "Cannot void while a dispute is active".
- Once the dispute process has fully closed, finalize() settles a surviving definite outcome, or opens 1:1 refunds if nothing is settleable — funds can never lock.

## 3. Source-level and lifecycle tests (deterministic, offline, no keys/network)
- One-source fallback -> UNRESOLVED, LLM not called: sim T7; tests/test_sources.py::test_one_source_fallback
- <2 sources or single domain rejected at creation: sim T1; tests/test_init_invariants.py
- Initial dispute window armed on resolution: sim T5; tests/test_dispute_lifecycle.py
- Both dispute rounds + exact 2-round limit: sim B3; tests/test_dispute_lifecycle.py
- Finalization at the deadline boundaries: sim T14–T17; tests/test_finalize_boundaries.py
- finalize() cannot bypass an active dispute: sim T17

## Proof (reproducible, no keys, no network)

    git clone https://github.com/Artem1981777/genlayer-prediction-market-v3
    cd genlayer-prediction-market-v3
    python3 sim_market.py

Expected: 101/101 checks pass. The gltest Direct-Mode suite under tests/ exercises the same behavior against the GenLayer runtime when the pinned genvm asset is available; sim_market.py is the self-contained proof that runs anywhere. The simulator now explicitly checks zero/one/two-source quorum, three-source fallback, conflicting admissible evidence, repeated finalization, `finalize()` during the initial window, round-one dispute, round-two dispute, and the post-dispute final-deadline path.

## On-chain note
The contract is not yet redeployed on Bradbury because the testnet is currently not activating deploy transactions (deploys time out without activation). The reproducible simulation is the primary proof; the contract will be redeployed once testnet deploy activation recovers.
