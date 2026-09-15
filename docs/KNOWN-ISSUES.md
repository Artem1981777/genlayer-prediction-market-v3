# Known Issues and Reproducible Workarounds

This repository pins `genlayer-test==0.29.2` for the direct Intelligent Contract tests. The deterministic CI gate intentionally runs `sim_market.py` on Python 3.12 because the two issues below affect the direct harness rather than the contract logic.

## 1. Direct-deploy clock can remain stale

**Symptom.** A test calls `direct_vm.warp(...)`, deploys a contract, and then the constructor or the first lifecycle call observes an earlier timestamp. The resulting assertion is typically `Resolution opens after the staking deadline` or `Final deadline has not passed yet`, even though the test has just warped beyond that deadline.

**Minimal reproduction.** In a direct test, deploy a market with a future `staking_deadline`, call `direct_vm.warp("2026-09-07T13:00:01.000Z")`, and immediately call `market.resolve()`. With the affected runner state, the contract sees the previous chain datetime.

**Workaround used here.** `tests/conftest.py` wraps `direct_vm.warp` and synchronizes both `genlayer.gl.message_raw` and `genlayer._internal.msg.message_raw` to the VM datetime. The simulator independently sets the same mocked chain datetime before every boundary assertion. This makes time behavior explicit and deterministic.

## 2. HTTP mock matching is protocol-sensitive

**Symptom.** `direct_vm.mock_web` may report an unused mock or return a failed load when the regular expression is written only for a host/path fragment, while the runner request includes a protocol-prefixed or normalized URL. The affected tests then observe zero admissible sources or a consensus mismatch.

**Minimal reproduction.** Register `mock_web(r"one\\.example", ...)` for a request configured as `https://one.example/evidence`, then inspect the runner warning that the web mock was never matched. Variants using `//one.example/` can fail similarly depending on the runner's request serialization.

**Workaround used here.** Direct tests register protocol-independent host patterns where possible and assert the contract's recorded verification counts. The authoritative no-network CI proof uses `sim_market.py`, whose `_Web.render` performs exact URL-key lookup for the same URLs stored in the frozen configuration. A failed load is represented explicitly by an absent page and is therefore covered by the one-source fallback tests.

## CI policy

GitHub Actions installs Python 3.12 and runs `python sim_market.py` on every push and pull request to `main`. The simulation is stdlib-only and exercises the exact contract source, including source binding, hostile disputant context, dispute deadlines, finalization, void boundaries, refunds, and the two-source quorum. Direct `pytest` tests remain available for a compatible GenLayer test runner and are not treated as a network-dependent CI gate.
