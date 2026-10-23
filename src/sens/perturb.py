from src.lp import solve_lp


def sensitivity(model,row,base=None,delta=0.01,tolerance=1e-6):
    if delta<=0: raise ValueError('delta must be positive')
    if row not in model.rows: raise ValueError(f'Unknown designated row {row}')
    base=base or solve_lp(model)
    minus=solve_lp(model.perturb(row,-delta)); plus=solve_lp(model.perturb(row,delta))
    left=(base.objective-minus.objective)/delta
    right=(plus.objective-base.objective)/delta
    price=float(base.pi[model.rows.index(row)])
    return {'row':row,'rhs':float(model.b[model.rows.index(row)]),'delta':delta,
            'z_minus':minus.objective,'z_base':base.objective,'z_plus':plus.objective,
            'left_slope':left,'price':price,'right_slope':right,
            'interval_passed':bool(left-tolerance<=price<=right+tolerance),
            'secants_differ':bool(abs(right-left)>tolerance)}
