import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
import scipy
import pulp
from src.model import build_model, instance_summary
from src.model.checkpoint3_generator_PUBLIC import cp34_instance
from src.lp import solve_lp, sign_calibration
from src.kkt import check_kkt, active_rows
from src.sens import sensitivity
from src.triangle import hand_results

ROOT=Path(__file__).resolve().parents[1]


def write_csv(path, records):
    if not records: return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0])); w.writeheader(); w.writerows(records)


def run(config_path,output_dir):
    cfg=json.loads(Path(config_path).read_text())
    if cfg['story'] not in ['A','B'] or cfg['variant'] not in [1,2,3]:
        raise ValueError('story and variant are invalid')
    call={k:cfg[k] for k in ['seed','story','variant']}
    if cfg.get('cap') is not None: call['cap']=cfg['cap']
    d=cp34_instance(**call); m=build_model(d); summary=instance_summary(d,m)
    official=cfg.get('official_check_values',{})
    for k,expected in official.items():
        if k not in summary: raise ValueError(f'Unknown check key {k}. Available {list(summary)}')
        if not np.isclose(summary[k],expected,atol=1e-9,rtol=0):
            raise ValueError(f'Check mismatch for {k}: {summary[k]} versus {expected}')
    calibration=sign_calibration(); sol=solve_lp(m); certificate=check_kkt(m,sol.x,sol.pi)
    if not certificate['passed']: raise AssertionError(certificate)
    sens=sensitivity(m,cfg['designated_row'],sol)
    if not sens['interval_passed']: raise AssertionError(sens)
    fractional=m.integer&(sol.x>1e-6)&(sol.x<1-1e-6)
    fractions=[{'variable':n,'value':float(v)} for n,v,f in zip(m.columns,sol.x,fractional) if f]
    centers=[v for v in fractions if v['variable'].startswith('y[')] if cfg['story']=='A' else []
    split_vms=sum(sum(sol.x[j]>1e-6 for j,n in enumerate(m.columns) if n.startswith(f'y[{k},'))>1 for k in range(d['M'])) if cfg['story']=='B' else 0
    table1={**summary,'zLP':sol.objective,'solver':'SciPy HiGHS','seconds':sol.seconds,
            'fractional_binary_variables':int(sum(fractional)),'split_vms':split_vms,
            'official_checks_supplied':bool(official)}
    tri=cfg['triangle']; hand=hand_results(tri['costs'],tri.get('prices'),tri.get('alternative_prices'))
    row_activity=active_rows(m,sol.x)
    for a in row_activity:
        a['nonzero_prices']=int(sum(abs(p)>1e-6 for p,f in zip(sol.pi,m.families) if f==a['family']))
    components={prefix:float(sum(c*x for c,x,n in zip(m.c,sol.x,m.columns) if n.startswith(prefix+'['))) for prefix in ['x','y','z','w','t']}
    result={'config':cfg,'call':call,'table1':table1,'table2':certificate,
            'table3':sens,'active_rows':row_activity,'fractional_centers':centers,'objective_components':components,
            'hand':hand,'calibration':calibration,
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'pulp':pulp.__version__}}
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'table1.csv',[table1])
    write_csv(out/'table2.csv',[{'condition':k,'maximum_error':v,'tolerance':1e-6,'passed':v<=1e-6} for k,v in certificate['numbers'].items()])
    write_csv(out/'table3.csv',[sens])
    write_csv(out/'active_rows.csv',result['active_rows'])
    write_csv(out/'fractional_variables.csv',fractions)
    write_csv(out/'solution.csv',[{'variable':n,'value':float(x),'reduced_cost':float(r),'lower':float(lo),'upper':float(hi)} for n,x,r,lo,hi in zip(m.columns,sol.x,sol.reduced,m.lower,m.upper)])
    ax=np.asarray(m.A@sol.x).ravel()
    write_csv(out/'row_prices.csv',[{'row':n,'family':f,'sense':s,'rhs':float(b),'lhs':float(a),'price':float(p)} for n,f,s,b,a,p in zip(m.rows,m.families,m.sense,m.b,ax,sol.pi)])
    write_csv(out/'triangle_binary_points.csv',hand['points'])
    # Portable solver-independent certificate inputs.
    np.savez_compressed(out/'certificate_vectors.npz',x=sol.x,pi=sol.pi)
    (out/'analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    manifests={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='sha256.json'}
    (out/'sha256.json').write_text(json.dumps(manifests,indent=2)+'\n')
    print(f'Instance {call}')
    print(f'Variables {len(m.c)}  rows {len(m.b)}')
    print(f'zLP {sol.objective:.6f}  fractional binaries {sum(fractional)}')
    print(f'KKT passed {certificate["passed"]}  sensitivity interval passed {sens["interval_passed"]}')
    print(f'Slopes {sens["left_slope"]:.9f}  price {sens["price"]:.9f}  {sens["right_slope"]:.9f}')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--config',default=str(ROOT/'team_config.json'))
    p.add_argument('--output',default=str(ROOT/'results'))
    a=p.parse_args(); run(a.config,a.output)
