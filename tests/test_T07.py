"""Independent checks against the assigned packet and a second LP solver."""
import json
from pathlib import Path
import numpy as np
import pulp
from src.model import build_model, instance_summary
from src.model.checkpoint3_generator_PUBLIC import cp34_instance
from src.lp import solve_lp
from src.kkt import check_kkt


def test_T07_packet_and_full_CBC_certificate():
    cfg = json.loads((Path(__file__).resolve().parents[1] / 'team_config.json').read_text())
    model = build_model(cp34_instance(cfg['seed'], cfg['story'], cfg['variant']))
    summary = instance_summary(cp34_instance(7, 'A', 2), model)
    for name, expected in cfg['official_check_values'].items():
        assert abs(summary[name] - expected) < 1e-6
    lp = pulp.LpProblem('T07_independent_check', pulp.LpMinimize)
    variables = [pulp.LpVariable(f'v{j}', lowBound=0, upBound=1)
                 for j in range(len(model.c))]
    lp += pulp.lpSum(float(c) * v for c, v in zip(model.c, variables))
    for i, rhs in enumerate(model.b):
        row = model.A.getrow(i)
        lhs = pulp.lpSum(float(a) * variables[int(j)] for j, a in zip(row.indices, row.data))
        lp += (lhs == float(rhs) if model.sense[i] == '=' else lhs <= float(rhs)), f'r{i}'
    assert lp.solve(pulp.PULP_CBC_CMD(msg=False)) == pulp.LpStatusOptimal
    x = np.array([v.value() for v in variables])
    pi = np.array([lp.constraints[f'r{i}'].pi for i in range(len(model.b))])
    # CBC serializes its solution at limited precision. Compare objectives with
    # relative tolerance 1e-8, stricter than the course's 1e-6 objective tolerance.
    # The small CBC test separately checks portability at absolute tolerance 1e-6.
    primary = solve_lp(model)
    assert abs(float(model.c @ x) - primary.objective) / max(1, abs(primary.objective)) < 1e-8
    assert check_kkt(model, primary.x, primary.pi)['passed']
