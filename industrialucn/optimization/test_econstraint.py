import logging
import sys
import unittest

import numpy as np

from . import econstraint as ec


def config_logger(logger, level):
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class EConstraint(unittest.TestCase):

    def test_cplex(self):
        from docplex.mp.model import Model as CplexModel

        config_logger(ec.logger, logging.DEBUG)

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
        mdl = CplexModel()

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

        pareto_frontier = []

        def extract_solution():
            xvals = {i: x[i].solution_value for i in parks}
            yvals = {(i, j): y[i, j].solution_value for i in buildings for j in parks}
            pareto_frontier.append((xvals, yvals))

        # run e-constraint
        ec.run_econstraint(model=mdl,
                           objectives=objectives,
                           solution_extractor=extract_solution,
                           optimizer='cplex')

        # print results
        for v in pareto_frontier:
            print(v)

    def test_run_econstraint_gurobi(self):
        from gurobipy import Model as GurobiModel
        from gurobipy import GRB, quicksum

        config_logger(ec.logger, logging.DEBUG)

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
        mdl = GurobiModel()

        # define variables
        x = mdl.addVars(parks, vtype=GRB.BINARY, name='x')
        y = mdl.addVars([(i, j) for i in buildings for j in parks], vtype=GRB.BINARY, name='y')
        z = mdl.addVars([0])[0]

        # define objective
        f1 = quicksum(-1 * x[i] for i in parks)
        f2 = quicksum(-1 * distance[i, j] * y[i, j] for i in buildings for j in parks)
        f3 = 0 - z
        objectives = [f1, f2, f3]

        # define constraints
        mdl.addConstrs(y[i, j] <= x[j] for i in buildings for j in parks)
        mdl.addConstrs(quicksum(y[i, j] for j in parks) >= 1 for i in buildings)
        mdl.addConstrs(distance[i, j] * y[i, j] <= z for i in buildings for j in parks)

        solutions = []

        def extract_solution():
            xvals = {i: x[i].x for i in parks}
            yvals = {(i, j): y[i, j].x for i in buildings for j in parks}
            solutions.append((xvals, yvals))

        ec.run_econstraint(model=mdl,
                           objectives=objectives,
                           solution_extractor=extract_solution,
                           optimizer='gurobi')

        print(solutions)


if __name__ == '__main__':
    unittest.main()
