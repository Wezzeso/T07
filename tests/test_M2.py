import numpy as np
from tests.common import hand
from src.triangle import A, triangle_model
from src.lp import solve_lp


def test_H2_half_point_rounding_and_gap():
    h=hand(); c=np.array(h['costs'])
    np.testing.assert_allclose(A@np.full(3,.5),np.ones(3),atol=1e-6)
    assert abs(h['zlp']-c.sum()/2)<1e-6
    assert np.all(A@np.ones(3)>=1)
    assert np.all(A@np.zeros(3)<1)
    z=solve_lp(triangle_model(c)).objective
    assert abs(z-h['zlp'])<1e-6
    assert abs(h['gap_integer_optimum']-(h['zstar']-z)/h['zstar'])<1e-6
    assert h['zstar']>z
