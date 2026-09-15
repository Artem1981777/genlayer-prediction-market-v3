# Evidence — GenLayer Prediction Market Resolver

Maps the steward's Sep 14 request to the exact contract logic and reproducible tests.

## Request addressed (Sep 14, Pavel Kolosov)
1. A definite YES/NO requires at least two independently binding-verified sources.
2. The final deadline cannot void a market while its dispute process is still active.
3. Source-level tests for one-source fallback, the initial dispute window, both dispute rounds, and finalization at deadline boundaries.

## Mapping

| Requirement | Contract location | Behavior | Proof |
|---|---|---|---|
| >=2 independent verified sources for a definite outcome | _resolve_now() (`verified_count < 2 or domain_count < 2`) | Forced UNRESOLVED, LLM not called | sim T7; tests/test_sources.py::test_one_source_fallback |
| >=2 sources from >=2 domains at creation | __init__ | Creation reverts otherwise | sim T1; tests/test_init_invariants.py |
| Final deadline never voids an active dispute | finalize() (`assert not dispute_active`) | Reverts while disputed / window open | sim T17; tests/test_finalize_boundaries.py |
| void() blocked during dispute | void() ("Cannot void while a dispute is active") | Reverts | sim T17 |
| Initial dispute window armed on resolution | resolve() (sets dispute_deadline) | status -> dispute_window | sim T5; tests/test_dispute_lifecycle.py |
| Exactly two dispute rounds | dispute() (`dispute_round < 2`) | Third dispute rejected | sim B3; tests/test_dispute_lifecycle.py |
| Finalization at deadline boundaries | finalize()/settle() | settle-or-void at final_deadline | sim T14–T17; tests/test_finalize_boundaries.py |

## Reproduce (no keys, no network)

    git clone https://github.com/Artem1981777/genlayer-prediction-market-v3
    cd genlayer-prediction-market-v3
    python3 sim_market.py

Expected output: 86/86 checks pass.

## On-chain status
Not yet redeployed on Bradbury (testnet deploy activation is timing out). The simulation is the self-contained primary proof; redeploy will follow once activation recovers.
