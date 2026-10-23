from tests.common import hand


def test_H5_three_relative_gaps():
    h=hand(); z=h['zlp']; c=h['costs']; zstar=h['zstar']
    assert z<=zstar
    assert abs(h['gap_integer_optimum']-(zstar-z)/zstar)<1e-6
    assert abs(h['gap_101']-(c[0]+c[2]-z)/(c[0]+c[2]))<1e-6
    assert abs(h['gap_111']-(sum(c)-z)/sum(c))<1e-6
