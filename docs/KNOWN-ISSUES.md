# Known Issues and Reproducible Workarounds

This file records the two environment/test-runner issues relevant to the v3 checklist. The first item was reported during the earlier setup work; the second was reproduced while running the newly expanded direct tests.

## 1. `pydantic-core` wheel availability depends on Python/platform

**Historical symptom.** On a Python/platform combination without a compatible prebuilt wheel, the minimal setup command fails during dependency installation with an error of this form:

```text
ERROR: Could not build wheels for pydantic-core, which is required to install pyproject.toml-based projects
error: can't find Rust compiler

This package requires Rust and Cargo to compile extensions. Install Rust or use a Python/platform combination with a compatible pydantic-core wheel.
```

**Minimal reproduction.** From a clean virtual environment, run:

```bash
python -m pip install genlayer-test==0.29.2
```

The failure is conditional: it occurs when the selected interpreter/platform has no matching `pydantic-core` wheel and pip falls back to a source build. It does **not** reproduce on the final GitHub Actions target used here (Ubuntu x86_64, Python 3.12): the exact command completed successfully and selected `pydantic_core-2.46.5-cp312-...manylinux...whl`.

**Workaround actually used.** Pin the test environment to Python 3.12 and install `genlayer-test==0.29.2` there, rather than attempting a Rust build in CI. If a local environment still lacks a wheel, either use the same Python/platform combination or install Rust/Cargo before retrying. No pydantic workaround is needed on the verified Linux x86_64 runner.

## 2. Pinned direct-test runner downloads a missing `genvm` release asset

**Exact symptom reproduced.** Installing the pinned packages succeeds on Python 3.12, but the first direct VM test tries to download a release asset that is no longer available:

```text
Downloading https://github.com/genlayerlabs/genvm/releases/download/v0.3.0-rc7/genvm-universal.tar.xz...
urllib.error.HTTPError: HTTP Error 404: Not Found
```

All 25 direct pytest tests fail at this setup step before contract assertions execute. This is a runner/fixture asset-availability problem, not a contract assertion failure.

**Minimal reproduction.** In a clean Python 3.12 environment:

```bash
pip install -r requirements-test.txt
pytest tests/ -q
```

The first direct VM fixture initialization requests the URL above and receives HTTP 404.

**Workaround actually used.** The CI gate runs the stdlib-only `python sim_market.py`, which loads the real contract source and does not require the unavailable `genvm` release asset. The direct tests remain in the repository for a compatible GenLayer test runner or a restored `v0.3.0-rc7` asset. No fake green pytest result is claimed.

## CI policy and successful run

GitHub Actions uses Python 3.12 and runs the deterministic simulator on every push and pull request to `main`. The successful run for commit `f40f3c0e6bddcb474a243d1afeb0aef4e5873fd9` is [GitHub Actions run 34969823046](https://github.com/Artem1981777/genlayer-prediction-market-v3/actions/runs/34969823046).
