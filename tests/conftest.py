import pytest

@pytest.fixture(autouse=True)
def configure_direct_mode(direct_vm):
    direct_vm.strict_mocks = True
    direct_vm.check_pickling = True
    return direct_vm
