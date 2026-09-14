import pytest

def deploy_market(direct_vm, direct_deploy, **overrides):
    cfg = {
        "s1": "https:" + "//one.example/evidence",
        "s2": "https:" + "//two.example/evidence",
        "b1": "Ethereum completed The Merge.",
        "b2": "The Merge completion is confirmed.",
        "w": 600,
        "sd": 1788786000,
        "fd": 1788787800,
    }
    cfg.update(overrides)
    direct_vm.warp("2026-09-07T12:00:00.000Z")
    return direct_deploy(
        "contracts/prediction_market.py",
        "Has Ethereum completed The Merge?",
        "Resolve YES if both sources confirm completion.",
        cfg["s1"],
        cfg["s2"],
        "",
        cfg["b1"],
        cfg["b2"],
        "",
        "init-test",
        cfg["w"],
        cfg["sd"],
        cfg["fd"],
    )

def test_full_dispute_deadline_invariant(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="final_deadline must leave room"):
        deploy_market(direct_vm, direct_deploy, fd=1788787799)

def test_requires_two_sources(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="At least two sources are required"):
        deploy_market(direct_vm, direct_deploy, s2="")

def test_requires_two_domains(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="at least two different domains"):
        deploy_market(direct_vm, direct_deploy, s2="https:" + "//m.one.example/evidence")

def test_rejects_short_binding(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="Every source needs a binding excerpt"):
        deploy_market(direct_vm, direct_deploy, b1="short")

def test_rejects_past_staking_deadline(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="Staking deadline must be in the future"):
        deploy_market(direct_vm, direct_deploy, sd=1788782400)

