import logging
from typing import Union, List, Dict

from docplex.mp.linear import LinearExpr
from docplex.mp.model import Model as CplexModel
from gurobipy import GRB, quicksum, LinExpr
from gurobipy import Model as GurobiModel

logger = logging.getLogger()


def _get_payoff_table_gurobi(mdl: GurobiModel, objectives):
    payoff_table = {}
    p = len(objectives)
    for k in range(p):
        logger.info(f'Entering loop, k={k}')
        mdl.setObjective(objectives[k], sense=GRB.MAXIMIZE)
        mdl.optimize()
        payoff_table[k, k] = mdl.ObjVal
        # noinspection PyArgumentList
        constraints = [mdl.addConstr(objectives[k] >= payoff_table[k, k])]
        for h in range(p):
            logger.info(f'Entering loop, h={h}')
            if h != k:
                mdl.setObjective(objectives[h], sense=GRB.MAXIMIZE)
                mdl.optimize()
                payoff_table[k, h] = mdl.ObjVal
                # noinspection PyArgumentList
                constraints.append(
                    mdl.addConstr(objectives[h] >= payoff_table[k, h])
                )
        logger.info(f'About to remove constraints, k={k}')
        mdl.remove(constraints)
    return payoff_table


def _get_payoff_table_cplex(mdl: CplexModel, objectives: List[LinearExpr]):
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


def get_payoff_table(mdl: Union[CplexModel, GurobiModel], objectives, optimizer=None):
    if optimizer == 'cplex':
        return _get_payoff_table_cplex(mdl, objectives)
    elif optimizer == 'gurobi':
        return _get_payoff_table_gurobi(mdl, objectives)
    else:
        raise NotImplementedError


def run_econstraint(mdl: Union[CplexModel, GurobiModel], objectives, g=None, optimizer=None):
    if optimizer == 'cplex':
        pot = _get_payoff_table_cplex(mdl, objectives)
        return _run_econstraint_cplex(mdl, objectives, pot, g)
    elif optimizer == 'gurobi':
        pot = _get_payoff_table_gurobi(mdl, objectives)
        return _run_econstraint_gurobi(mdl, objectives, pot, g)
    else:
        raise NotImplementedError


def _run_econstraint_gurobi(mdl: GurobiModel, objectives: List[LinExpr], payoff_table, g=None, sol_extractor=None):
    p = len(objectives)
    s = mdl.addVars([k for k in range(1, p)], name='s')
    lb = {k: min(payoff_table[h, k] for h in range(p))
          for k in range(1, p)}
    r = {k: max(payoff_table[h, k] for h in range(p)) - min(payoff_table[h, k] for h in range(p))
         for k in range(1, p)}
    logger.debug('r: %s', r)
    epsilon = 1e-3
    mdl.setObjective(objectives[0] + epsilon * quicksum(s[k] / r[k] for k in range(1, p)), sense=GRB.MAXIMIZE)
    if g is None:
        g = {k: 3 for k in range(1, p)}  # default number of grid
        logger.warning('using default grid g=3')
    i = {k: 0 for k in range(1, p)}
    while True:
        e = {k: lb[k] + (i[k] * r[k]) / g[k] for k in range(1, p)}
        logger.info(f'i: {i}, e: {e}')
        constraints = mdl.addConstrs(objectives[k] - s[k] == e[k] for k in range(1, p))
        mdl.optimize()
        if mdl.SolCount > 0:
            sol_extractor()
            logger.info('feasible')
        else:
            logger.info('not feasible')
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


def _run_econstraint_cplex(mdl: CplexModel, objectives, payoff_table, g: Dict[int, int] = None, sol_extractor=None):
    assert isinstance(g, int)
    assert g >= 2
    p = len(objectives)
    s = mdl.continuous_var_dict([k for k in range(1, p)], name='s')
    lb = {k: min(payoff_table[h, k] for h in range(p))
          for k in range(1, p)}
    r = {k: max(payoff_table[h, k] for h in range(p)) - min(payoff_table[h, k] for h in range(p))
         for k in range(1, p)}
    logger.debug('r: %s', r)
    epsilon = 1e-3
    mdl.maximize(objectives[0] + epsilon * mdl.sum(s[k] / r[k] for k in range(1, p)))
    if g is None:
        g = {k: 3 for k in range(1, p)}  # default number of grid
        logger.warning('using default grid g=3')
    i = {k: 0 for k in range(1, p)}
    while True:
        e = {k: lb[k] + (i[k] * r[k]) / g[k] for k in range(1, p)}
        logger.info(f'i: {i}, e: {e}')
        constraints = mdl.add_constraints(objectives[k] - s[k] == e[k] for k in range(1, p))
        solution = mdl.solve()
        if solution is not None:
            sol_extractor()
            logger.info('feasible')
        else:
            logger.info('not feasible')
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
