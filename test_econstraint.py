import logging

import numpy as np
from docplex.mp.model import Model

from orlabucn.econstraint import get_payoff_table, run_econstraint

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

# define parameters
n = 15  # number of parks
m = 50  # number of buildings
rnd = np.random
rnd.seed(0)
cpx = rnd.rand(n) * 300  # x coordinate for parks
cpy = rnd.rand(n) * 100  # y coordinate for parks
cbx = rnd.rand(m) * 300  # x coordinate for buildings
cby = rnd.rand(m) * 100  # y coordinate for buildings
parks = [i for i in range(n)]
buildings = [j for j in range(m)]
distance = {(i, j): np.hypot(cbx[i] - cpx[j], cby[i] - cpy[j])
            for i in buildings for j in parks}

# define model
mdl = Model()

# define variables
x = mdl.binary_var_dict(parks, name='x')
y = mdl.binary_var_dict([(i, j) for i in buildings for j in parks], name='y')

# define objective
f1 = -mdl.sum(x[i] for i in parks)
f2 = -mdl.sum(distance[i, j] * y[i, j] for i in buildings for j in parks)
f3 = -mdl.max(distance[i, j] * y[i, j] for i in buildings for j in parks)
objectives = [f1, f2, f3]

# define constraints
mdl.add_constraints(y[i, j] <= x[j] for i in buildings for j in parks)
mdl.add_constraints(mdl.sum(y[i, j] for j in parks) >= 1 for i in buildings)

# run e-constraint
payoff_table = get_payoff_table(mdl, objectives)
pareto_frontier = run_econstraint(mdl, objectives, payoff_table)

# print results
print(payoff_table)
for v in pareto_frontier:
    print([v.get_value(o) for o in objectives])
