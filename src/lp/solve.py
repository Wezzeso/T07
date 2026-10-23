from dataclasses import dataclass
from time import perf_counter
import numpy as np
from scipy.optimize import linprog


@dataclass
class Solution:
    x: np.ndarray
    pi: np.ndarray
    reduced: np.ndarray
    objective: float
    seconds: float
    iterations: int


def solve_lp(model):
    """Return prices in ORIGINAL senses, including nonnegative prices for >=."""
    eq = np.flatnonzero(model.sense == '=')
    ineq = np.flatnonzero(model.sense != '=')
    signs = np.where(model.sense[ineq] == '>=', -1.0, 1.0)
    start = perf_counter()
    r = linprog(model.c, A_ub=model.A[ineq].multiply(signs[:,None]).tocsr() if len(ineq) else None,
                b_ub=model.b[ineq]*signs if len(ineq) else None,
                A_eq=model.A[eq] if len(eq) else None, b_eq=model.b[eq] if len(eq) else None,
                bounds=list(zip(model.lower,model.upper)),method='highs',
                options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    elapsed = perf_counter()-start
    if not r.success:
        raise RuntimeError(f'LP solve failed status {r.status}: {r.message}')
    pi = np.zeros(len(model.b))
    pi[eq] = r.eqlin.marginals
    pi[ineq] = r.ineqlin.marginals*signs
    reduced = model.c-np.asarray(model.A.T@pi).ravel()
    return Solution(r.x,pi,reduced,float(r.fun),elapsed,int(r.nit))


def sign_calibration():
    # Known optimum (1,1), z=3. Increasing the <= RHS improves z at rate -1.
    # min -x+4y with x<=1, y>=1 and x,y>=0 has original prices (-1,4).
    r=linprog([-1.,4.],A_ub=[[1.,0.],[0.,-1.]],b_ub=[1.,-1.],bounds=[(0,None),(0,None)],method='highs')
    if not r.success: raise RuntimeError(r.message)
    original_prices=np.array([r.ineqlin.marginals[0],-r.ineqlin.marginals[1]])
    assert np.allclose(r.x,[1,1],atol=1e-9)
    assert np.allclose(original_prices,[-1,4],atol=1e-9)
    return {'objective':float(r.fun),'x':r.x.tolist(),'prices':original_prices.tolist()}
