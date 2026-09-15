import pytest


def make_market(direct_vm, direct_deploy):
    direct_vm.warp("2026-09-07T12:00:00.000Z")
    return direct_deploy(
        "contracts/prediction_market.py", "Has Ethereum completed The Merge?",
        "Resolve YES if both sources confirm completion.",
        "https:" + "//one.example/evidence", "https:" + "//two.example/evidence", "",
        "Ethereum completed The Merge.", "The Merge completion is confirmed.", "",
        "void-boundary", 600, 1788786000, 1788787800)


def fund(market, direct_vm, direct_alice):
    direct_vm.deal(direct_alice, 1000)
    direct_vm.value = 100
    with direct_vm.prank(direct_alice):
        market.stake("YES")
    direct_vm.value = 0


def test_void_before_and_at_staking_deadline(direct_vm, direct_deploy, direct_alice):
    market = make_market(direct_vm, direct_deploy)
    fund(market, direct_vm, direct_alice)
    direct_vm.warp("2026-09-07T12:59:59.000Z")
    with pytest.raises(AssertionError, match="cannot void before staking_deadline"):
        market.void()
    direct_vm.warp("2026-09-07T13:00:00.000Z")
    market.void()
    assert market.get_state()["status"] == "voided"


def test_void_unresolved_dispute_phases_and_rejects_definite_outcome(direct_vm, direct_deploy, direct_alice):
    market = make_market(direct_vm, direct_deploy)
    fund(market, direct_vm, direct_alice)
    direct_vm.warp("2026-09-07T13:00:00.000Z")
    market.void()
    assert market.get_state()["status"] == "voided"

    market = make_market(direct_vm, direct_deploy)
    fund(market, direct_vm, direct_alice)
    direct_vm.mock_web(r"one\.example", {"method": "GET", "status": 200, "body": "unrelated"})
    direct_vm.mock_web(r"two\.example", {"method": "GET", "status": 200, "body": "unrelated"})
    direct_vm.warp("2026-09-07T13:00:00.000Z")
    market.resolve()
    market.void()
    assert market.get_state()["status"] == "voided"

    market = make_market(direct_vm, direct_deploy)
    fund(market, direct_vm, direct_alice)
    direct_vm.mock_web(r"one\.example", {"method": "GET", "status": 200, "body": "Ethereum completed The Merge."})
    direct_vm.mock_web(r"two\.example", {"method": "GET", "status": 200, "body": "The Merge completion is confirmed."})
    direct_vm.mock_llm(r"neutral prediction-market resolver", '{"outcome":"YES"}')
    direct_vm.warp("2026-09-07T13:00:01.000Z")
    market.resolve()
    with pytest.raises(AssertionError, match="Cannot void a market with a definite YES/NO outcome"):
        market.void()
