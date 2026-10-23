import numpy as np


def check_kkt(model, x, pi, tolerance=1e-6):
    """Solver independent LP certificate using original row senses and actual bounds.

    A fixed variable has no reduced cost sign restriction. Its bound support
    contribution is its fixed value times r. This handles B2/B3 forbidden pairs.
    """
    x, pi = np.asarray(x,float),np.asarray(pi,float)
    if x.shape != model.c.shape or pi.shape != model.b.shape:
        raise ValueError('x and pi must match the model column and row counts')
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(pi)):
        raise ValueError('certificate vectors must be finite')
    ax=np.asarray(model.A@x).ravel()
    residual=model.b-ax
    eq=model.sense=='='; le=model.sense=='<='; ge=model.sense=='>='
    max0=lambda a:float(np.max(a,initial=0))
    primal=max(max0(abs(residual[eq])),max0(-residual[le]),max0(residual[ge]),
               max0(model.lower-x),max0(x-model.upper))
    dual=max(max0(pi[le]),max0(-pi[ge]))
    row_cs=max0(abs(pi*residual))
    r=model.c-np.asarray(model.A.T@pi).ravel()
    fixed=np.isfinite(model.upper)&(model.upper==model.lower)
    at_lower=(x<=model.lower+tolerance)&~fixed
    at_upper=(x>=model.upper-tolerance)&~fixed
    interior=~(fixed|at_lower|at_upper)
    reduced=max(max0(-r[at_lower]),max0(r[at_upper]),max0(abs(r[interior])))
    # min_{lower <= v <= upper} r^T v is the bound term in the dual.
    # An unbounded-above variable with negative r has no finite bound minimum.
    finite=np.isfinite(model.upper)
    support=float(np.sum(model.lower*np.maximum(r,0))+np.sum(model.upper[finite]*np.minimum(r[finite],0)))
    dual_value=float(model.b@pi+support)
    if np.any(r[~finite]<-tolerance): dual_value=float('-inf')
    primal_value=float(model.c@x)
    gap=abs(primal_value-dual_value)
    numbers={'a_primal':primal,'b_dual_signs':dual,'c_row_complementarity':row_cs,
             'd_reduced_costs':reduced,'e_strong_duality':gap}
    return {'numbers':numbers,'passed':all(v<=tolerance for v in numbers.values()),
            'primal_value':primal_value,'dual_value':dual_value,
            'signed_primal_minus_dual':primal_value-dual_value,'tolerance':tolerance}


def active_rows(model,x,tolerance=1e-6):
    slack=abs(model.b-np.asarray(model.A@x).ravel())
    return [{'family':f,'active':int(np.sum(slack[np.array(model.families)==f]<=tolerance)),
             'total':model.families.count(f)} for f in dict.fromkeys(model.families)]
