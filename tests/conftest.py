import sys, pytest
def _s(v):
    for n in ("genlayer.gl","genlayer._internal.msg"):
        m=sys.modules.get(n)
        r=getattr(m,"message_raw",None) if m else None
        if isinstance(r,dict): r["datetime"]=v._datetime
@pytest.fixture(autouse=True)
def configure_direct_mode(direct_vm):
    direct_vm.strict_mocks=True
    direct_vm.check_pickling=True
    w=direct_vm.warp
    def f(t):
        w(t)
        _s(direct_vm)
    direct_vm.warp=f
    return direct_vm
