# GenLayer Prediction Market Resolver

A GenLayer Intelligent Contract that runs a full prediction-market lifecycle: staking, permissionless resolution from cited immutable web sources, a mandatory dispute process, settlement, and a hard-deadline exit. The contract also has a **phase-gated `void()`** that cannot cancel a funded market while it is still open for staking.

This repository is the v3 evidence repository for the steward review and EditResubmit workflow.

- **Live site:** https://artem1981777.github.io/genlayer-prediction-market-v3/
- **Chain:** GenLayer Testnet Bradbury (Chain ID 4221)
- **Contract:** `contracts/prediction_market.py`
- **Evidence response:** [`docs/REVIEW-RESPONSE-2.md`](docs/REVIEW-RESPONSE-2.md)
- **Final technical report:** [`docs/FINAL-REPORT.md`](docs/FINAL-REPORT.md)
- **Final response text:** [`docs/FINAL-RESPONSE.md`](docs/FINAL-RESPONSE.md)
- **Latest commit:** `930e8af1bde1d9781f6169220ecba3de325d128d`
- **Primary proof:** offline consensus simulation — **101/101 checks pass**
- **Latest green CI:** [GitHub Actions run 34980827937](https://github.com/Artem1981777/genlayer-prediction-market-v3/actions/runs/34980827937)

## Current progress

The v3 implementation now covers the complete permissionless lifecycle and the requested steward-review hardening. The deterministic simulator loads the real contract source, replaces only the GenLayer runtime with a local mock, and exercises the same source-binding, consensus, dispute, settlement, refund, and finalization paths used by the contract.

| Area | Current status | Evidence |
|---|---|---|
| Immutable source configuration | Complete: constructor validates URLs, excerpts, deadlines, source count, domain independence, hashes, and frozen config | `contracts/prediction_market.py`, `tests/test_init_invariants.py` |
| Definite outcome quorum | Complete: `YES`/`NO` requires at least two admissible, binding-verified sources from at least two registrable domains | Simulator T6/T7/T7b/T7c; `tests/test_sources.py` |
| Failed or inadmissible evidence | Complete: failed loads, missing excerpts, and same-domain evidence are excluded; one verified source remains `UNRESOLVED` | Simulator T6/T7/T7b; `tests/test_sources.py` |
| Dispute lifecycle | Complete: initial window plus at most two dispute rounds, with explicit deadline boundaries | Simulator T5/T9/T10/B3/T17b; `tests/test_dispute_lifecycle.py` |
| Active-dispute finalization | Complete: `finalize()` cannot void or settle while the initial window or either dispute round is active | Simulator T17/T17b; `tests/test_finalize_boundaries.py` |
| Deadline and repeat safety | Complete: exact deadlines, pre-deadline rejection, post-process settlement, and repeated-finalize rejection are covered | Simulator T14–T17b; `tests/test_finalize_boundaries.py` |
| `void()` safety | Complete: permissionless but blocked before `staking_deadline`, during active disputes, and for definite outcomes | Simulator T18/T19; `tests/test_void_boundaries.py` |
| Hostile context | Complete: disputant prompt injection cannot override deterministic admissibility or binding checks | Simulator T10b; `tests/test_security_boundaries.py` |
| CI | Green on Python 3.12 with the deterministic simulator | [CI run 34980827937](https://github.com/Artem1981777/genlayer-prediction-market-v3/actions/runs/34980827937) |

## Steward review — Sep 9 void phase-gate

**Concern:** Any account could call `void()` while a funded market was open, before the staking deadline, and cancel it before resolution.

**Fix:** `void()` remains permissionless, but while `status == "open"` it requires `now >= staking_deadline`. Before that point it reverts with:

```text
market still open for staking, cannot void before staking_deadline
```

A definite `YES` or `NO` outcome can never be voided. An unresolved market can be voided after the staking phase, opening 1:1 refunds. An active dispute cannot be voided.

## Steward review — Sep 14 two-source and dispute-finalization request

The Sep 14 request from Pavel Kolosov required that a definite result use at least two independently binding-verified sources and that the final deadline never bypass an active dispute process. Both properties are enforced by the contract and now have explicit behavioral coverage:

1. `_resolve_now()` excludes failed or unbound sources and returns `UNRESOLVED` before the LLM when fewer than two admissible sources or fewer than two independent domains remain. A single valid source cannot determine the market outcome.
2. `finalize()` rejects while `status == "disputed"` or while the current `dispute_window` / `dispute_resolved` phase remains before its deadline. Only after all dispute processing is complete can settlement or deadline void occur.

Detailed source references and test mapping are in [`docs/REVIEW-RESPONSE-2.md`](docs/REVIEW-RESPONSE-2.md) and [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

## Contract lifecycle

| Method | Access | Notes |
|---|---|---|
| `__init__(...)` | deploy | validates and freezes config: at least 2 sources, at least 2 domains, binding excerpts, and future deadlines |
| `stake(side)` | payable, anyone | records a positive stake while `now < staking_deadline` |
| `resolve()` | anyone | after `staking_deadline` with at least one staker; resolves only from admissible, binding-verified evidence |
| `dispute()` | staked participants | opens one of at most two dispute rounds before the current deadline |
| `resolve_dispute()` | anyone | permissionlessly advances an active dispute and opens its next configured window |
| `settle()` | anyone | settles only after the current dispute window closes; auto-voids if the winning side has no stake |
| `finalize()` | anyone | after `final_deadline`, settles only when no dispute process is active; otherwise it reverts |
| `void()` | anyone | permissionless, phase-gated: never while open for staking, during an active dispute, or on a definite outcome |
| `claim()` | winners | pari-mutuel payout after settlement |
| `refund()` | stakers | single-use 1:1 refund after voiding |

Every consensus-critical decision is computed and stored by the contract. No owner-only lifecycle authority is used.

## Verification

### Deterministic simulator

The simulator requires only Python 3 and no keys or network access:

```bash
git clone https://github.com/Artem1981777/genlayer-prediction-market-v3
cd genlayer-prediction-market-v3
python3 sim_market.py
```

Expected result:

```text
CHECKS: 101  PASSED: 101  FAILED: 0
```

The 101 checks include zero/one/two-source quorum, three-source fallback, conflicting admissible evidence, initial and both dispute rounds, exact deadline behavior, active-dispute finalization, repeated-finalize safety, refunds, hostile-context defense, and the phase-gated `void()` path.

### Direct GenLayer tests

The repository contains **25 pytest test functions** under `tests/`. The pinned packages install successfully under Python 3.12, but the current `genlayer-test==0.29.2` runner requests an unavailable external asset before the tests reach their assertions:

```text
Downloading https://github.com/genlayerlabs/genvm/releases/download/v0.3.0-rc7/genvm-universal.tar.xz...
urllib.error.HTTPError: HTTP Error 404: Not Found
```

This is an environment limitation, not a claimed green pytest result. The exact reproduction and workaround are documented in [`docs/KNOWN-ISSUES.md`](docs/KNOWN-ISSUES.md). The deterministic simulator is the authoritative no-network contract proof used by CI.

### CI

The workflow is configured in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) and runs the simulator on Python 3.12 for pushes and pull requests to `main`. The latest successful run is [34980827937](https://github.com/Artem1981777/genlayer-prediction-market-v3/actions/runs/34980827937).

## On-chain status

The gated v3 contract has not yet been redeployed on Bradbury because deploy activation has been timing out on the testnet. Earlier deployments predate the current hardening and are intentionally not linked as proof of the fixed behavior. The static live site reflects the fixed source but makes no on-chain calls.

Deploy tooling is included for when testnet activation recovers:

```bash
npm install
node --env-file=.env deploy.mjs
```

This requires a funded `PRIVATE_KEY` in `.env`; see [`.env.example`](.env.example).

## Repository layout

```text
contracts/prediction_market.py   Intelligent Contract implementation
sim_market.py                    deterministic 101-check simulator
tests/                           25 direct test functions
docs/EVIDENCE.md                 requirement-to-proof mapping
docs/REVIEW-RESPONSE.md          consolidated review response
docs/REVIEW-RESPONSE-2.md        Sep 14 EditResubmit response
docs/KNOWN-ISSUES.md              reproducible test-runner limitations
.github/workflows/ci.yml          Python 3.12 CI workflow
index.html                       static live-site overview
```

## Recent meaningful commits

- `95bdfa7` — expand quorum and dispute boundary verification; add conflicting-evidence, three-source, and repeated-finalize scenarios.
- `6236e6e` — cover every active dispute phase at finalization, including both dispute rounds.
- `91d9e6c` — record the final green CI evidence and pinned review-response links.
- `98370f3` — document the test-runner issues and create the Sep 14 review response.
- `f40f3c0` — add the Python 3.12 CI workflow and complete the steward checklist.

## License

MIT — see [`LICENSE`](LICENSE).
