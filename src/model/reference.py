from dataclasses import dataclass, replace
import numpy as np
from scipy.sparse import coo_matrix


@dataclass
class Model:
    c: np.ndarray
    A: object
    b: np.ndarray
    sense: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    columns: list
    rows: list
    families: list
    integer: np.ndarray

    def perturb(self, row, change):
        i = self.rows.index(row)
        b = self.b.copy()
        b[i] += change
        return replace(self, b=b)


def build_model(d):
    """Build exactly the handout formulation. Bounds are never counted as rows."""
    costs, lower, upper, columns, integer = [], [], [], [], []
    rr, cc, vv, rhs, senses, rows, families = [], [], [], [], [], [], []

    def col(name, cost=0, ub=1, binary=True):
        j = len(costs)
        costs.append(cost); lower.append(0.0); upper.append(ub)
        columns.append(name); integer.append(binary)
        return j

    def row(name, family, terms, sense, b):
        i = len(rhs)
        for j, a in terms:
            if a != 0:
                rr.append(i); cc.append(j); vv.append(float(a))
        rows.append(name); families.append(family); senses.append(sense); rhs.append(b)

    variant = d['variant']
    if d['story'] == 'A':
        N, V = d['N'], d['V']
        x = {(i,k): col(f'x[{i},{k}]', d['dist'][i,k]) for i in range(N) for k in range(N)}
        y = [col(f'y[{k}]', 0 if variant == 3 else 2*d['D'][k]) for k in range(N)]
        z = {i: col(f'z[{i}]', d['penalty'][i]) for i in range(N)
             if variant == 2 and d['is_premium'][i]}
        w = {(k,j): col(f'w[{k},{j}]', 2*d['D'][k]*d['vehicle_cost_per_km'][j])
             for k in range(N) for j in range(V)} if variant == 3 else {}
        for i in range(N):
            terms = [(x[i,k], 1) for k in range(N)]
            if i in z: terms.append((z[i], 1))
            row(f'A1[{i}]', 'A1', terms, '=', 1)
        for i in range(N):
            for k in range(N):
                row(f'A2[{i},{k}]', 'A2', [(x[i,k],1), (y[k],-1)], '<=', 0)
        for k in range(N):
            terms = [(x[i,k],d['demand'][i]) for i in range(N)]
            terms += [(w[k,j],-d['vehicle_cap'][j]) for j in range(V)] if variant == 3 else [(y[k],-d['Cap'])]
            row(f'A3[{k}]', 'A3', terms, '<=', 0)
            row(f'A4[{k}]', 'A4', [(x[k,k],1),(y[k],-1)], '=', 0)
        if variant == 3:
            for k in range(N):
                row(f'A6[{k}]', 'A6', [(y[k],1)]+[(w[k,j],-1) for j in range(V)], '=', 0)
            for j in range(V):
                row(f'A7[{j}]', 'A7', [(w[k,j],1) for k in range(N)], '=', 1)
        else:
            row('A5', 'A5', [(j,1) for j in y], '=', V)
    elif d['story'] == 'B':
        M, S = d['M'], d['S']
        y = {}
        for k in range(M):
            for l in range(S):
                forbidden = (variant == 2 and d['vm_required_zone'][k] != -1 and d['zone'][l] != d['vm_required_zone'][k]) or (variant == 3 and d['needs_gpu'][k] and not d['is_gpu_server'][l])
                y[k,l] = col(f'y[{k},{l}]', ub=0 if forbidden else 1)
        t = [col(f't[{l}]',1,np.inf,False) for l in range(S)]
        for k in range(M):
            row(f'B1[{k}]','B1',[(y[k,l],1) for l in range(S)],'=',1)
        for l in range(S):
            row(f'B2[{l}]','B2',[(y[k,l],d['cpu_req'][k]) for k in range(M)],'<=',d['cpu_cap'][l])
            row(f'B3[{l}]','B3',[(y[k,l],d['mem_req'][k]) for k in range(M)],'<=',d['mem_cap'][l])
            for m,u in enumerate((0.0,0.4,0.7,0.9)):
                a, beta = 1/(1-u)**2, -u*u/(1-u)**2
                row(f'B4[{l},{m}]','B4',[(t[l],1)]+[(y[k,l],-a*d['cpu_req'][k]/d['cpu_cap'][l]) for k in range(M)],'>=',beta)
    else:
        raise ValueError('story must be A or B')
    return Model(np.array(costs,float), coo_matrix((vv,(rr,cc)),shape=(len(rhs),len(costs))).tocsr(),
                 np.array(rhs,float),np.array(senses),np.array(lower),np.array(upper),columns,rows,families,np.array(integer,bool))


def instance_summary(d, model):
    summary = {'variables': len(model.c), 'rows': len(model.b),
               'nonzeros':model.A.nnz, 'fixed_zero_variables':int(np.sum(model.upper == 0))}
    for key in ['N','V','M','S','Cap']:
        if key in d: summary[key] = int(d[key])
    for key in ['demand','cpu_req','mem_req','cpu_cap','mem_cap','vehicle_cap','is_premium','is_premium_vm','needs_gpu','is_gpu_server']:
        if key in d: summary[key+'_sum'] = int(np.sum(d[key]))
    if 'dist' in d:
        summary['distance_sum_3dp'] = round(float(np.sum(d['dist'])), 3)
    return summary
