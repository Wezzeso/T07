import numpy as np
import pytest
import pulp
from src.model import build_model
from src.model.checkpoint3_generator_PUBLIC import cp34_instance
from src.lp import solve_lp
from src.kkt import check_kkt


@pytest.mark.parametrize('story,variant',[('A',1),('A',2),('A',3),('B',1),('B',2),('B',3)])
def test_all_reference_variants_sizes_and_certificates(story,variant):
    d=cp34_instance(2026,story,variant); m=build_model(d)
    if story=='A':
        n,v=d['N'],d['V']
        cols=n*n+n+(int(sum(d['is_premium'])) if variant==2 else n*v if variant==3 else 0)
        rows=n*n+4*n+v if variant==3 else n*n+3*n+1
    else:
        cols=d['M']*d['S']+d['S']; rows=d['M']+6*d['S']
    assert len(m.c)==cols and len(m.b)==rows
    s=solve_lp(m)
    assert check_kkt(m,s.x,s.pi)['passed']
    if story=='B' and variant in [2,3]:
        assert np.all(s.x[m.upper==0]==0)


def test_capacity_override_changes_only_capacity_rows():
    a=build_model(cp34_instance(2026,'A',1))
    b=build_model(cp34_instance(2026,'A',1,cap=123))
    assert a.rows==b.rows and a.columns==b.columns
    np.testing.assert_allclose(a.c,b.c)
    changed=np.unique((a.A-b.A).nonzero()[0])
    assert all(a.families[i]=='A3' for i in changed)


def test_external_cbc_solution_passes_solver_independent_checker():
    # A small B3 model deliberately includes upper-bound-zero GPU pairs.
    d={'story':'B','variant':3,'M':3,'S':2,'cpu_req':np.array([1,2,1]),
       'mem_req':np.array([1,1,2]),'cpu_cap':np.array([4,5]),'mem_cap':np.array([5,5]),
       'needs_gpu':np.array([1,0,1]),'is_gpu_server':np.array([1,0])}
    m=build_model(d)
    problem=pulp.LpProblem('external_certificate',pulp.LpMinimize)
    vs=[pulp.LpVariable(f'v{j}',lowBound=float(m.lower[j]),upBound=float(m.upper[j]) if np.isfinite(m.upper[j]) else None) for j in range(len(m.c))]
    problem+=pulp.lpSum(float(c)*v for c,v in zip(m.c,vs))
    for i in range(len(m.b)):
        ar=m.A.getrow(i); lhs=pulp.lpSum(float(a)*vs[int(j)] for j,a in zip(ar.indices,ar.data))
        constraint=lhs==float(m.b[i]) if m.sense[i]=='=' else lhs<=float(m.b[i]) if m.sense[i]=='<=' else lhs>=float(m.b[i])
        problem+=constraint,f'r{i}'
    status=problem.solve(pulp.PULP_CBC_CMD(msg=False))
    assert status==pulp.LpStatusOptimal
    x=np.array([v.value() for v in vs]); pi=np.array([problem.constraints[f'r{i}'].pi for i in range(len(m.b))])
    cert=check_kkt(m,x,pi)
    assert cert['passed'],cert
    assert abs(m.c@x-solve_lp(m).objective)<1e-6
