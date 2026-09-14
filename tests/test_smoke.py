def test_direct_deploy(direct_vm, direct_deploy):
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
