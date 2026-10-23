import numpy as np
from scipy.sparse import csr_matrix
from src.model import Model
from src.kkt import check_kkt
from src.sens import sensitivity


def test_fixed_zero_column_allows_negative_reduced_cost():
    # x0 cannot move despite its negative cost. It contributes zero to the dual.
    m=Model(np.array([-2.,1.]),csr_matrix([[0.,1.]]),np.array([1.]),np.array(['>=']),
            np.zeros(2),np.array([0.,1.]),['fixed','free'],['cover'],['cover'],np.ones(2,bool))
    result=check_kkt(m,[0,1],[1])
    assert result['passed']
    assert result['dual_value']==1


def test_upper_bound_support_is_included_in_dual_value():
    # With no structural rows, min -x over [0,1] is certified solely by the bound.
    m=Model(np.array([-1.]),csr_matrix((0,1)),np.array([]),np.array([],str),
            np.zeros(1),np.ones(1),['x'],[],[],np.ones(1,bool))
    result=check_kkt(m,[1],[])
    assert result['passed']
    assert result['dual_value']==-1


def test_sensitivity_detects_a_known_nondifferentiable_optimum():
    # min x with x>=b and x>=0 gives z(b)=max(0,b), with a kink at b=0.
    m=Model(np.array([1.]),csr_matrix([[1.]]),np.array([0.]),np.array(['>=']),
            np.zeros(1),np.array([np.inf]),['x'],['cover'],['cover'],np.zeros(1,bool))
    result=sensitivity(m,'cover')
    assert result['interval_passed'] and result['secants_differ']
    assert abs(result['left_slope'])<1e-6
    assert abs(result['right_slope']-1)<1e-6
    assert 0<=result['price']<=1
