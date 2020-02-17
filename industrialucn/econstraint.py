import logging

from docplex.mp.model import Model


def get_payoff_table(mdl: Model, objectives):
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


def run_econstraint(mdl: Model, objectives, payoff_table, g=None):
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
