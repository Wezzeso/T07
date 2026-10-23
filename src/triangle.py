"""Analytic hand-task calculations. No reference-model data are changed here."""
from itertools import product
import numpy as np
from scipy.sparse import csr_matrix
from src.model import Model
from src.kkt import check_kkt

A = np.array([[1.,1.,0.],[0.,1.,1.],[1.,0.,1.]])


def triangle_model(costs):
    c=np.array(costs,float)
    if c.shape!=(3,) or np.any(c<=0): raise ValueError('three positive costs required')
    return Model(c,csr_matrix(A),np.ones(3),np.array(['>=']*3),np.zeros(3),np.ones(3),
                 ['y1','y2','y3'],['T1','T2','T3'],['T1','T2','T3'],np.ones(3,bool))


def hand_results(costs,prices=None,alternative_prices=None):
    m=triangle_model(costs)
    p=np.linalg.solve(A.T,m.c) if prices is None else np.asarray(prices,float)
    if np.min(p)<0: raise ValueError('half point is not certified by these dual prices')
    pp=0.8*p if alternative_prices is None else np.asarray(alternative_prices,float)
    points=[]
    for y in product([0,1],repeat=3):
        points.append({'point':list(y),'feasible':bool(np.all(A@np.array(y)>=1)),
                       'cost':float(m.c@np.array(y))})
    zstar=min(v['cost'] for v in points if v['feasible'])
    zlp=float(sum(m.c)/2)
    x=np.full(3,0.5)
    return {'costs':m.c.tolist(),'A':A.tolist(),'b':[1,1,1],'points':points,
            'prices':p.tolist(),'alternative_prices':pp.tolist(),'zlp':zlp,'zstar':zstar,
            'half_certificate':check_kkt(m,x,p),'alternative_certificate':check_kkt(m,x,pp),
            'alternative_bound':check_kkt(m,x,pp)['dual_value'],
            'alternative_bound_loss':zlp-check_kkt(m,x,pp)['dual_value'],
            'gap_integer_optimum':(zstar-zlp)/zstar,
            'gap_101':(float(m.c@[1,0,1])-zlp)/float(m.c@[1,0,1]),
            'gap_111':(sum(m.c)-zlp)/sum(m.c),
            'epsilon_interval':[-1,1], 'sensitivity_slope':float(p[0])}
