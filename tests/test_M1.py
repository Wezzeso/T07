import numpy as np
from tests.common import hand
from src.triangle import A


def test_H1_matrix_signs_and_enumeration():
    h=hand()
    assert A.shape==(3,3)
    assert len(h['points'])==8
    assert sum(p['feasible'] for p in h['points'])==4
    c=np.array(h['costs'])
    # For positive costs, the cheapest feasible binary point chooses two items.
    expected=min(c[0]+c[1],c[1]+c[2],c[0]+c[2])
    assert abs(h['zstar']-expected)<1e-6
    p=np.array(h['prices'])
    np.testing.assert_allclose((-A).T@(-p),A.T@p,atol=1e-6)
    assert np.all(-p<=0)
