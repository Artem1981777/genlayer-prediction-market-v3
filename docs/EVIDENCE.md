# Evidence — GenLayer Prediction Market Resolver

Maps the steward's Sep 14 request and the remaining v3 checklist to reproducible source-level proofs.

## Request addressed (Sep 14, Pavel Kolosov)

1. A definite YES/NO requires at least two independently binding-verified sources.
2. The final deadline cannot void a market while its configured dispute process is still active.
3. Source-level tests cover one-source fallback, the initial dispute window, both dispute rounds, and finalization at deadline boundaries.

## Mapping

| Requirement | Contract location | Behavior | Proof |
|---|---|---|---|
| >=2 independent verified sources for a definite outcome | `_resolve_now()` (`verified_count < 2 or domain_count < 2`) | Forces `UNRESOLVED`; LLM is not called below threshold | `sim_market.py` T7; `tests/test_sources.py::test_one_source_fallback` |
| >=2 sources from >=2 domains at creation | `__init__` | Creation reverts otherwise | `tests/test_init_invariants.py` source/domain boundary cases |
| Final deadline never voids an active dispute | `finalize()` (`assert not dispute_active`) | Reverts while disputed or a configured window is open | `sim_market.py` T17; `tests/test_finalize_boundaries.py` |
| `void()` blocked during dispute | `void()` | Reverts for `status == disputed` | `sim_market.py` T17; `tests/test_finalize_boundaries.py` |
| Initial dispute window armed on resolution | `resolve()` | `status -> dispute_window` and deadline is set | `sim_market.py` T5; `tests/test_dispute_lifecycle.py` |
| Exactly two dispute rounds | `dispute()` (`dispute_round < 2`) | Third dispute rejected | `sim_market.py` B3; `tests/test_dispute_lifecycle.py` |
| Finalization at deadline boundaries | `finalize()` / `settle()` | Exact deadline succeeds; one second early reverts | `sim_market.py` T14–T17; `tests/test_finalize_boundaries.py` |
| Constructor length, URL, binding, deadline, hash invariants | `__init__` | Boundary values are accepted/rejected precisely | `tests/test_init_invariants.py` (11 tests) |
| Non-staker cannot dispute | `dispute()` participant guard | Reverts with the exact participant-only message | `tests/test_security_boundaries.py::test_non_staker_cannot_dispute`; simulator T9 |
| Hostile LLM/disputant context | `_resolve_now()` deterministic binding gate and untrusted context prompt | Injection cannot create an outcome without admissible evidence | `tests/test_security_boundaries.py::test_prompt_injection_context_cannot_bypass_binding_gate`; `sim_market.py` T10b |
| `void()` boundary behavior | `void()` staking/status/outcome gates | Reverts at `staking_deadline - 1`, succeeds at `staking_deadline`, rejects definite YES/NO | `tests/test_void_boundaries.py`; `sim_market.py` T19 |
| Reproducible runner limitations | test harness / CI policy | Known clock and URL-mock workarounds are explicit | [`docs/KNOWN-ISSUES.md`](KNOWN-ISSUES.md) |

## Reproduce locally

```bash
git clone https://github.com/Artem1981777/genlayer-prediction-market-v3
cd genlayer-prediction-market-v3
python3 sim_market.py
```

Expected result after this change: **87/87 checks pass**. The simulation has no network or API-key dependency and loads the real contract source.

For direct tests, install the pinned requirements in `requirements-test.txt` and run `pytest -q`. The direct harness requires a compatible GenLayer test environment; its two observed 0.29.2 limitations and the workarounds used here are recorded in [`docs/KNOWN-ISSUES.md`](KNOWN-ISSUES.md).

## CI proof

The workflow at [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs on push and pull request to `main`, uses **Python 3.12**, and executes the deterministic simulator. The successful run URL should be appended here after GitHub Actions completes:

> CI run: pending GitHub Actions execution for this commit.

No successful remote run can be truthfully linked from the local checkout before Actions executes the pushed commit.
