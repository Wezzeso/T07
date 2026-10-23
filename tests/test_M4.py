import numpy as np
from tests.common import hand
from src.triangle import triangle_model
from src.lp import solve_lp
from src.sens import sensitivity


def test_H4_rhs_formula_and_validity_interval():
    h=hand(); m=triangle_model(h['costs'])
    for eps in [-1,-.25,0,.01,.25,1]:
        y=np.array([(1+eps)/2,(1+eps)/2,(1-eps)/2])
        assert np.min(y)>=0 and np.max(y)<=1
        np.testing.assert_allclose(m.A@y,[1+eps,1,1],atol=1e-6)
        expected=h['zlp']+h['prices'][0]*eps
        assert abs(m.c@y-expected)<1e-6
        assert abs(solve_lp(m.perturb('T1',eps)).objective-expected)<1e-6
    s=sensitivity(m,'T1')
    assert s['interval_passed']
    assert abs(s['left_slope']-h['prices'][0])<1e-6
    assert abs(s['right_slope']-h['prices'][0])<1e-6
    for eps in [-1.01,1.01]:
        y=np.array([(1+eps)/2,(1+eps)/2,(1-eps)/2])
        assert np.min(y)<0 or np.max(y)>1
