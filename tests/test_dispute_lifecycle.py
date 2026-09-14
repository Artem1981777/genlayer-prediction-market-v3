import pytest

def test_initial_dispute_boundaries(direct_vm, direct_deploy, direct_alice):
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


    snapshot = direct_vm.snapshot()
    deadline = state["dispute_deadline"]
    direct_vm.warp("2026-09-07T13:10:00.000Z")
    with pytest.raises(AssertionError, match="Dispute window is still open"):
        market.settle()
    with direct_vm.prank(direct_alice):
        market.dispute("Boundary challenge.")
    assert market.get_state()["status"] == "disputed"
    direct_vm.revert(snapshot)
    direct_vm.warp("2026-09-07T13:10:01.000Z")
    with direct_vm.prank(direct_alice):
        with pytest.raises(AssertionError, match="Dispute window has closed"):
            market.dispute("Too late.")
    market.settle()
    assert market.get_state()["status"] == "settled"


def test_two_dispute_rounds(direct_vm, direct_deploy, direct_alice):
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
    deadline1 = state["dispute_deadline"]
    direct_vm.warp("2026-09-07T13:10:00.000Z")
    with direct_vm.prank(direct_alice):
        market.dispute("Round one.")
    state = market.get_state()
    assert state["dispute_round"] == 1
    direct_vm.warp("2026-09-07T13:10:01.000Z")
    market.resolve_dispute()
    state = market.get_state()
    assert state["status"] == "dispute_resolved"
    assert state["dispute_outcome"] == "UPHELD"
    assert state["dispute_round"] == 1
    deadline2 = state["dispute_deadline"]
    direct_vm.warp("2026-09-07T13:20:00.000Z")
    with direct_vm.prank(direct_alice):
        market.dispute("Round two.")
    state = market.get_state()
    assert state["dispute_round"] == 2
    direct_vm.clear_mocks()
    direct_vm.mock_web(r"one\.example", {"method": "GET", "status": 200, "body": "Ethereum completed The Merge."})
    direct_vm.mock_web(r"two\.example", {"method": "GET", "status": 200, "body": "The Merge completion is confirmed."})
    direct_vm.mock_llm(r"neutral prediction-market resolver", '{"outcome":"NO"}')
    direct_vm.warp("2026-09-07T13:20:01.000Z")
    market.resolve_dispute()
    state = market.get_state()
    assert state["status"] == "dispute_resolved"
    assert state["outcome"] == "NO"
    assert state["dispute_outcome"] == "OVERTURNED"
    assert state["dispute_round"] == 2
    direct_vm.warp("2026-09-07T13:30:00.000Z")
    with direct_vm.prank(direct_alice):
        with pytest.raises(AssertionError, match="^Dispute limit reached$"):
            market.dispute("Round three.")
    state = market.get_state()
    assert state["status"] == "dispute_resolved"
    assert state["dispute_round"] == 2
