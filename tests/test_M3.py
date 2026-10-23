import numpy as np
from tests.common import hand
from src.triangle import triangle_model
from src.kkt import check_kkt
from src.lp import sign_calibration


def test_H3_full_and_weaker_dual_certificates():
    h=hand(); m=triangle_model(h['costs']); x=np.full(3,.5)
    good=check_kkt(m,x,h['prices']); bad=check_kkt(m,x,h['alternative_prices'])
    assert good['passed']
    for v in good['numbers'].values(): assert v<=1e-6
    pp=np.array(h['alternative_prices']); r=m.c-m.A.T@pp
    assert np.all(pp>=0) and np.all(r>=-1e-6)
    assert bad['numbers']['a_primal']<=1e-6
    assert bad['numbers']['b_dual_signs']<=1e-6
    assert bad['numbers']['c_row_complementarity']<=1e-6
    assert abs(bad['numbers']['d_reduced_costs']-max(abs(r)))<1e-6
    assert abs(bad['numbers']['e_strong_duality']-h['alternative_bound_loss'])<1e-6
    assert h['alternative_bound']<=h['zlp']+1e-6


def test_solver_price_signs_are_calibrated():
    p=sign_calibration()
    np.testing.assert_allclose(p['prices'],[-1,4],atol=1e-6)


def test_checker_rejects_forged_primal_and_prices():
    h=hand(); m=triangle_model(h['costs'])
    assert not check_kkt(m,[0,0,0],h['prices'])['passed']
    assert not check_kkt(m,[.5,.5,.5],[-10,-10,-10])['passed']
