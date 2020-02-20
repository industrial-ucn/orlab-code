import logging
from typing import Union

from docplex.mp.model import Model as CplexModel
from gurobipy import GRB
from gurobipy import Model as GurobiModel


def get_payoff_table_gurobi(mdl: GurobiModel, objectives):
    payoff_table = {}
    p = len(objectives)
    for k in range(p):
        print(f'Entering loop, k={k}')
        mdl.setObjective(objectives[k], sense=GRB.MAXIMIZE)
        mdl.optimize()
        payoff_table[k, k] = mdl.ObjVal
        # noinspection PyArgumentList
        constraints = [mdl.addConstr(objectives[k] >= payoff_table[k, k])]
        for h in range(p):
            print(f'Entering loop, h={h}')
            if h != k:
                mdl.setObjective(objectives[h], sense=GRB.MAXIMIZE)
                mdl.optimize()
                payoff_table[k, h] = mdl.ObjVal
                # noinspection PyArgumentList
                constraints.append(
                    mdl.addConstr(objectives[h] >= payoff_table[k, h])
                )
        print(f'About to remove constraints, k={k}')
        mdl.remove(constraints)
    return payoff_table


def get_payoff_table_cplex(mdl: CplexModel, objectives):
    payoff_table = {}
    p = len(objectives)
    for k in range(p):
        mdl.maximize(objectives[k])
        solution = mdl.solve()
        payoff_table[k, k] = solution.get_objective_value()
        constraints = [mdl.add_constraint(objectives[k] >= payoff_table[k, k])]
        for h in range(p):
            if h != k:
                mdl.maximize(objectives[h])
                solution = mdl.solve()
                payoff_table[k, h] = solution.get_objective_value()
                constraints.append(
                    mdl.add_constraint(objectives[h] >= payoff_table[k, h])
                )
        mdl.remove(constraints)
    return payoff_table


def run_econstraint(mdl: Union[CplexModel, GurobiModel], objectives, g=None, optimizer='cplex'):
    if optimizer == 'cplex':
        pot = get_payoff_table_cplex(mdl, objectives)
        return run_econstraint_cplex(mdl, objectives, pot, g)
    else:
        pot = get_payoff_table_gurobi(mdl, objectives)
        return pot  # TODO implement for gurobi


def run_econstraint_cplex(mdl: CplexModel, objectives, payoff_table, g=None):
    p = len(objectives)
    s = mdl.continuous_var_dict([k for k in range(1, p)], name='s')
    lb = {k: min(payoff_table[h, k] for h in range(p))
          for k in range(1, p)}
    r = {k: max(payoff_table[h, k] for h in range(p)) - min(payoff_table[h, k] for h in range(p))
         for k in range(1, p)}
    logging.debug('r: %s', r)
    epsilon = 1e-3
    mdl.maximize(objectives[0] + epsilon * mdl.sum(s[k] / r[k] for k in range(1, p)))
    if g is None:
        g = {k: 3 for k in range(1, p)}  # default number of grid
        logging.warning('using default grid g=3')
    i = {k: 0 for k in range(1, p)}
    frontier = []
    while True:
        e = {k: lb[k] + (i[k] * r[k]) / g[k] for k in range(1, p)}
        print(i)
        print(e)
        constraints = mdl.add_constraints(objectives[k] - s[k] == e[k] for k in range(1, p))
        solution = mdl.solve()
        if solution is not None:
            frontier.append(solution)
            print('feasible')
        else:
            print('not feasible')
        mdl.remove(constraints)
        if all(i[k] == g[k] for k in range(1, p)):
            break
        else:
            for k in range(1, p):
                if i[k] == g[k]:
                    i[k] = 0
                else:
                    i[k] += 1
                    break
    return frontier
