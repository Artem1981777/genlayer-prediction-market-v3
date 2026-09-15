# Final Technical Report

## Scope

This report records the final state of the GenLayer Prediction Market Resolver v3 after addressing the Sep 14 steward request from Pavel Kolosov. The requested properties are enforced by the contract and verified by a deterministic simulator that loads the real contract source.

## Implemented behavior

A definite `YES` or `NO` requires at least two admissible sources that pass the deterministic binding-excerpt check and come from at least two independent registrable domains. Failed loads, missing or non-matching excerpts, and same-domain evidence do not count. If fewer than two admissible sources remain, `_resolve_now()` returns `UNRESOLVED` before invoking the LLM. A final defense-in-depth check prevents an invalid consensus payload from producing a definite outcome.

`finalize()` is blocked while the initial dispute window, a submitted first dispute, or a submitted second dispute remains active. At `now == dispute_deadline`, the current window is closed and the next lifecycle operation may proceed according to the phase. At `now < dispute_deadline`, settlement and finalization remain blocked. At `final_deadline`, finalization still cannot bypass a currently active dispute. After all dispute processing is complete, a definite outcome can settle; an unresolved outcome can safely enter the refund-enabled void path. Repeated finalization after settlement or voiding is rejected without changing state.

## Verification results

| Check | Result |
|---|---:|
| Deterministic simulator | **101/101 passed** |
| Python compilation (`py_compile`) | Passed |
| Formatting/error whitespace (`git diff --check`) | Passed |
| Python direct tests discovered | 25 test functions |
| Direct pytest execution | Blocked before assertions by missing `genvm` release asset |
| GitHub Actions simulator CI | **Success** |
| CI Python version | 3.12 |

The direct runner failure is reproducible with the pinned environment:

```text
Downloading https://github.com/genlayerlabs/genvm/releases/download/v0.3.0-rc7/genvm-universal.tar.xz...
urllib.error.HTTPError: HTTP Error 404: Not Found
```

This is documented in [`KNOWN-ISSUES.md`](KNOWN-ISSUES.md). It does not affect the deterministic simulator or its no-network execution.

## Evidence

- Repository: https://github.com/Artem1981777/genlayer-prediction-market-v3
- Latest commit: `930e8af1bde1d9781f6169220ecba3de325d128d`
- Latest green CI: [run 34982476830](https://github.com/Artem1981777/genlayer-prediction-market-v3/actions/runs/34982476830)
- Review response: [`REVIEW-RESPONSE-2.md`](REVIEW-RESPONSE-2.md)
- Requirement mapping: [`EVIDENCE.md`](EVIDENCE.md)
- Runner limitations: [`KNOWN-ISSUES.md`](KNOWN-ISSUES.md)

## Remaining external step

The GenLayer Portal submission still contains the original v2 evidence links until EditResubmit is completed. The technical work is present in v3; the portal evidence must be replaced with v3 repository links, preferably pinned to the final commit that contains the submitted evidence.
