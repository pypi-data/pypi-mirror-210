from .get_utms import ALL_UTMS
import pytest

TESTS = [(name, 'standard') for name in ALL_UTMS.keys()] + [(name, 'double') for name in ALL_UTMS.keys()] + [(name, 'eights') for name in ALL_UTMS]

@pytest.mark.parametrize("name,precision", TESTS)
def test_fqir_runtime(name, precision):
    ALL_UTMS[name].test_fqir_runtime(bw_conf=precision)