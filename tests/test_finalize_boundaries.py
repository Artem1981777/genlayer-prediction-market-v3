import pytest

def test_finalize_open_market_boundaries(direct_vm, direct_deploy, direct_alice):
    direct_vm.warp("2026-09-07T12:00:00.000Z")
    market = direct_deploy(
        "contracts/prediction_market.py",
        "Has Ethereum completed The Merge?",
        "Resolve YES if both sources confirm completion.",
        "https:" + "//one.example/evidence",
        "https:" + "//two.example/evidence",
        "",
        "Ethereum completed The Merge.",
        "The Merge completion is confirmed.",
        "",
        "smoke",
        600,
        1788786000,
        1788868800,
    )
    state = market.get_state()
    assert state["status"] == "open"
    assert state["dispute_round"] == 0
    direct_vm.deal(direct_alice, 1000)
    direct_vm.value = 100
    with direct_vm.prank(direct_alice):
        market.stake("YES")
    direct_vm.value = 0
    direct_vm.warp("2026-09-08T11:59:59.000Z")
    with pytest.raises(AssertionError, match="Final deadline has not passed yet"):
        market.finalize()
    direct_vm.warp("2026-09-08T12:00:00.000Z")
    market.finalize()
    state = market.get_state()
    assert state["status"] == "voided"
    assert state["void_reason"] == "deadline_void"
    with direct_vm.prank(direct_alice):
        refunded = market.refund()
    assert refunded == 100


def test_finalize_rejects_disputed_status(direct_vm, direct_deploy, direct_alice):
    direct_vm.warp("2026-09-07T12:00:00.000Z")
    market = direct_deploy(
        "contracts/prediction_market.py",
        "Has Ethereum completed The Merge?",
        "Resolve YES if both sources confirm completion.",
        "https:" + "//one.example/evidence",
        "https:" + "//two.example/evidence",
        "",
        "Ethereum completed The Merge.",
        "The Merge completion is confirmed.",
        "",
        "smoke",
        600,
        1788786000,
        1788868800,
    )
    state = market.get_state()
    assert state["status"] == "open"
    assert state["dispute_round"] == 0
    direct_vm.deal(direct_alice, 1000)
    direct_vm.value = 100
    with direct_vm.prank(direct_alice):
        market.stake("YES")
    direct_vm.value = 0
    direct_vm.mock_web(r"one\.example", {"method": "GET", "status": 200, "body": "Ethereum completed The Merge."})
    direct_vm.mock_web(r"two\.example", {"method": "GET", "status": 200, "body": "The Merge completion is confirmed."})
    direct_vm.mock_llm(r"neutral prediction-market resolver", '{"outcome":"YES"}')
    direct_vm.warp("2026-09-07T13:00:01.000Z")
    market.resolve()
    state = market.get_state()
    assert state["status"] == "dispute_window"
    assert state["outcome"] == "YES"
    assert state["last_verified_count"] == 2
    assert state["last_verified_domains"] == 2
    assert direct_vm.run_validator() is not False
    direct_vm.warp("2026-09-07T13:10:00.000Z")
    with direct_vm.prank(direct_alice):
        market.dispute("Active dispute.")
    direct_vm.warp("2026-09-08T12:00:00.000Z")
    with pytest.raises(AssertionError, match="dispute process still active"):
        market.finalize()
    with pytest.raises(AssertionError, match="Cannot void while a dispute is active"):
        market.void()
    assert market.get_state()["status"] == "disputed"


def test_finalize_settles_yes(direct_vm, direct_deploy, direct_alice):
    direct_vm.warp("2026-09-07T12:00:00.000Z")
    market = direct_deploy(
        "contracts/prediction_market.py",
        "Has Ethereum completed The Merge?",
        "Resolve YES if both sources confirm completion.",
        "https:" + "//one.example/evidence",
        "https:" + "//two.example/evidence",
        "",
        "Ethereum completed The Merge.",
        "The Merge completion is confirmed.",
        "",
        "smoke",
        600,
        1788786000,
        1788868800,
    )
    state = market.get_state()
    assert state["status"] == "open"
    assert state["dispute_round"] == 0
    direct_vm.deal(direct_alice, 1000)
    direct_vm.value = 100
    with direct_vm.prank(direct_alice):
        market.stake("YES")
    direct_vm.value = 0
    direct_vm.mock_web(r"one\.example", {"method": "GET", "status": 200, "body": "Ethereum completed The Merge."})
    direct_vm.mock_web(r"two\.example", {"method": "GET", "status": 200, "body": "The Merge completion is confirmed."})
    direct_vm.mock_llm(r"neutral prediction-market resolver", '{"outcome":"YES"}')
    direct_vm.warp("2026-09-07T13:00:01.000Z")
    market.resolve()
    state = market.get_state()
    assert state["status"] == "dispute_window"
    assert state["outcome"] == "YES"
    assert state["last_verified_count"] == 2
    assert state["last_verified_domains"] == 2
    assert direct_vm.run_validator() is not False


    direct_vm.warp("2026-09-08T12:00:00.000Z")
    market.finalize()
    state = market.get_state()
    assert state["status"] == "settled"
    assert state["winning_side"] == "YES"
    with direct_vm.prank(direct_alice):
        payout = market.claim()
    assert payout == 100
