import hashlib

import pytest


def deploy_market(direct_vm, direct_deploy, **overrides):
    cfg = {
        "q": "Has Ethereum completed The Merge?",
        "r": "Resolve YES if both sources confirm completion.",
        "s1": "https:" + "//one.example/evidence",
        "s2": "https:" + "//two.example/evidence",
        "s3": "",
        "b1": "Ethereum completed The Merge.",
        "b2": "The Merge completion is confirmed.",
        "b3": "",
        "w": 600,
        "sd": 1788786000,
        "fd": 1788787800,
    }
    cfg.update(overrides)
    direct_vm.warp("2026-09-07T12:00:00.000Z")
    return direct_deploy(
        "contracts/prediction_market.py", cfg["q"], cfg["r"],
        cfg["s1"], cfg["s2"], cfg["s3"], cfg["b1"], cfg["b2"], cfg["b3"],
        "init-test", cfg["w"], cfg["sd"], cfg["fd"],
    )


def test_question_and_rules_length_boundaries(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="Question must be 8..500 chars"):
        deploy_market(direct_vm, direct_deploy, q="q" * 7)
    deploy_market(direct_vm, direct_deploy, q="q" * 8)
    deploy_market(direct_vm, direct_deploy, q="q" * 500)
    with pytest.raises(AssertionError, match="Question must be 8..500 chars"):
        deploy_market(direct_vm, direct_deploy, q="q" * 501)
    with pytest.raises(AssertionError, match="Rules must be 8..1000 chars"):
        deploy_market(direct_vm, direct_deploy, r="r" * 7)
    deploy_market(direct_vm, direct_deploy, r="r" * 8)
    deploy_market(direct_vm, direct_deploy, r="r" * 1000)
    with pytest.raises(AssertionError, match="Rules must be 8..1000 chars"):
        deploy_market(direct_vm, direct_deploy, r="r" * 1001)


def test_source_url_and_binding_boundaries(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match=r"http\(s\) URLs"):
        deploy_market(direct_vm, direct_deploy, s2="ftp://two.example/evidence")
    with pytest.raises(AssertionError, match="Source URL too long"):
        deploy_market(direct_vm, direct_deploy, s2="https://two.example/" + "x" * 500)
    with pytest.raises(AssertionError, match="Every source needs a binding excerpt"):
        deploy_market(direct_vm, direct_deploy, b1="b" * 7)
    with pytest.raises(AssertionError, match="Every source needs a binding excerpt"):
        deploy_market(direct_vm, direct_deploy, b1="b" * 401)


def test_requires_two_sources_and_two_registrable_domains(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="At least two sources are required"):
        deploy_market(direct_vm, direct_deploy, s2="")
    with pytest.raises(AssertionError, match="at least two different domains"):
        deploy_market(direct_vm, direct_deploy, s2="https://m.one.example/evidence")


def test_deadline_boundaries(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="Dispute window must be a positive"):
        deploy_market(direct_vm, direct_deploy, w=0)
    with pytest.raises(AssertionError, match="Staking deadline must be in the future"):
        deploy_market(direct_vm, direct_deploy, sd=1788782400)
    with pytest.raises(AssertionError, match="Final deadline must be after"):
        deploy_market(direct_vm, direct_deploy, fd=1788786000)
    with pytest.raises(AssertionError, match="final_deadline must leave room"):
        deploy_market(direct_vm, direct_deploy, fd=1788787799)


def test_hashes_strip_input_and_config_hash_is_deterministic(direct_vm, direct_deploy):
    first = deploy_market(direct_vm, direct_deploy,
                          q="  Has Ethereum completed The Merge?  ",
                          r="  Resolve YES if both sources confirm completion.  ")
    second = deploy_market(direct_vm, direct_deploy,
                           q="  Has Ethereum completed The Merge?  ",
                           r="  Resolve YES if both sources confirm completion.  ")
    a, b = first.get_state(), second.get_state()
    assert a["question_hash"] == hashlib.sha256(a["question"].encode()).hexdigest()
    assert a["rules_hash"] == hashlib.sha256(a["rules"].encode()).hexdigest()
    assert a["question_hash"] == b["question_hash"]
    assert a["rules_hash"] == b["rules_hash"]
    assert a["frozen_config_hash"] == b["frozen_config_hash"]


def test_valid_boundary_configuration_still_deploys(direct_vm, direct_deploy):
    market = deploy_market(direct_vm, direct_deploy, w=1, fd=1788786003)
    assert market.get_state()["status"] == "open"


def test_requires_two_sources_legacy_case(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="At least two sources are required"):
        deploy_market(direct_vm, direct_deploy, s2="")


def test_requires_two_domains_legacy_case(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="at least two different domains"):
        deploy_market(direct_vm, direct_deploy, s2="https://m.one.example/evidence")


def test_rejects_short_binding_legacy_case(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="Every source needs a binding excerpt"):
        deploy_market(direct_vm, direct_deploy, b1="short")


def test_rejects_past_staking_deadline_legacy_case(direct_vm, direct_deploy):
    with pytest.raises(AssertionError, match="Staking deadline must be in the future"):
        deploy_market(direct_vm, direct_deploy, sd=1788782400)
