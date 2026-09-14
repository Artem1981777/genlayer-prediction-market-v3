def test_one_source_fallback(direct_vm, direct_deploy, direct_alice):
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
    direct_vm.mock_web(r"one\.example", {"method": "GET", "status": 200, "body": "Unrelated page."})
    direct_vm.mock_web(r"two\.example", {"method": "GET", "status": 200, "body": "The Merge completion is confirmed."})
    direct_vm.warp("2026-09-07T13:00:01.000Z")
    market.resolve()
    state = market.get_state()
    assert state["status"] == "open"
    assert state["outcome"] == "UNRESOLVED"
    assert state["last_verified_count"] == 1
    assert state["last_verified_domains"] == 1
    assert direct_vm.run_validator() is not False


def test_two_sources_two_domains_verified(direct_vm, direct_deploy, direct_alice):
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


def test_two_sources_same_domain_verified(direct_vm, direct_deploy, direct_alice):
    direct_vm.warp("2026-09-07T12:00:00.000Z")
    market = direct_deploy(
        "contracts/prediction_market.py",
        "Has Ethereum completed The Merge?",
        "Resolve YES if both sources confirm completion.",
        "https:" + "//one.example/evidence",
        "https:" + "//m.one.example/evidence",
        "https:" + "//two.example/evidence",
        "Ethereum completed The Merge.",
        "The Merge completion is confirmed.",
        "Independent source binding must stay absent.",
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
    direct_vm.mock_web(r"//one\.example/", {"method": "GET", "status": 200, "body": "Ethereum completed The Merge."})
    direct_vm.mock_web(r"//m.one.example/", {"method": "GET", "status": 200, "body": "The Merge completion is confirmed."})
    direct_vm.mock_web(r"two\.example", {"method": "GET", "status": 200, "body": "The Merge completion is confirmed."})
    direct_vm.warp("2026-09-07T13:00:01.000Z")
    market.resolve()
    state = market.get_state()
    assert state["status"] == "open"
    assert state["outcome"] == "UNRESOLVED"
    assert state["last_verified_count"] == 2
    assert state["last_verified_domains"] == 1
    assert direct_vm.run_validator() is not False


def test_three_sources_one_failed_load(direct_vm, direct_deploy, direct_alice):
    direct_vm.warp("2026-09-07T12:00:00.000Z")
    market = direct_deploy(
        "contracts/prediction_market.py",
        "Has Ethereum completed The Merge?",
        "Resolve YES if both sources confirm completion.",
        "https:" + "//one.example/evidence",
        "https:" + "//two.example/evidence",
        "https:" + "//three.example/evidence",
        "Ethereum completed The Merge.",
        "The Merge completion is confirmed.",
        "Third source should fail to load.",
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


def test_validator_disagrees_on_binding(direct_vm, direct_deploy, direct_alice):
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
    snapshot = direct_vm.snapshot()
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
    direct_vm.clear_mocks()


    direct_vm.mock_web(r"one\.example", {"method": "GET", "status": 200, "body": "Binding removed."})
    direct_vm.mock_web(r"two\.example", {"method": "GET", "status": 200, "body": "Binding removed."})
    direct_vm._gl_call_hook = lambda vm, request: {"ok": False} if "ExecPromptTemplate" in request else None
    assert direct_vm.run_validator() is False
    direct_vm.revert(snapshot)
    state = market.get_state()
    assert state["status"] == "open"
    assert state["outcome"] == ""
