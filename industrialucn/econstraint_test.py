import logging
import sys
import unittest

import numpy as np

from industrialucn import econstraint as ec


def config_logger(logger, level):
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


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


class EConstraint(unittest.TestCase):

    def test_dominance(self):
        v1 = [[1.0, 4324.8, 165.4],
              [2.0, 2757.5, 116.1],
              [3.0, 2106.9, 74.8],
              [13.0, 1351.1, 56.9],
              [2.0, 2757.5, 116.1],
              [2.0, 2966.0, 107.7],
              [3.0, 2106.9, 74.8],
              [13.0, 1351.1, 56.9]]

        v2 = [[1.0, 4324.8, 165.4],
              [2.0, 2757.5, 116.1],
              [3.0, 2106.9, 74.8],
              [13.0, 1351.1, 56.9],
              [2.0, 2757.5, 116.1],
              [2.0, 2966.0, 107.7],
              [3.0, 2106.9, 74.8],
              [13.0, 1351.1, 56.9],
              [3.0, 2223.9, 82.5]]

        v3 = [[1.0, 4324.8, 165.4],
              [2.0, 2757.5, 116.1],
              [3.0, 2106.9, 74.8],
              [13.0, 1351.1, 56.9],
              [2.0, 2757.5, 116.1],
              [2.0, 2966.0, 107.7],
              [3.0, 2106.9, 74.8],
              [13.0, 1351.1, 56.9],
              [3.0, 2223.9, 82.5],
              [2.0, 2106.9, 74.8]]

        self.assertTrue(ec.all_non_dominated(v1))
        self.assertFalse(ec.all_non_dominated(v2))
        self.assertFalse(ec.all_non_dominated(v3))

        self.assertTrue(ec.all_weakly_non_dominated(v1))
        self.assertTrue(ec.all_weakly_non_dominated(v2))
        self.assertFalse(ec.all_weakly_non_dominated(v3))

    def test_run_econstraint_cplex_mip(self):
        from docplex.mp.model import Model as CplexModel

        config_logger(ec.logger, logging.DEBUG)

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

        def f(i, sol):
            x, y = sol
            if i == 0:
                return sum(x[i] for i in parks)
            elif i == 1:
                return sum(distance[i, j] * y[i, j] for i in buildings for j in parks)
            else:
                return max(distance[i, j] * y[i, j] for i in buildings for j in parks)

        fvs = [[f(i, sol) for i in range(3)] for sol in pareto_frontier]

        for fv in fvs:
            a, b, c = fv
            print(f'[{a:>5.1f}, {b:>7.1f}, {c:>5.1f}],')

        self.assertTrue(ec.all_weakly_non_dominated(fvs))

    def test_run_econstraint_cplex_lp(self):
        from docplex.mp.model import Model as CplexModel

        config_logger(ec.logger, logging.DEBUG)

        # define model
        mdl = CplexModel()

        # define variables
        x = mdl.continuous_var_dict(parks, name='x')
        y = mdl.continuous_var_dict([(i, j) for i in buildings for j in parks], name='y')

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

        def f(i, sol):
            x, y = sol
            if i == 0:
                return sum(x[i] for i in parks)
            elif i == 1:
                return sum(distance[i, j] * y[i, j] for i in buildings for j in parks)
            else:
                return max(distance[i, j] * y[i, j] for i in buildings for j in parks)

        fvs = [[f(i, sol) for i in range(3)] for sol in pareto_frontier]

        for fv in fvs:
            a, b, c = fv
            print(f'[{a:>5.1f}, {b:>7.1f}, {c:>5.1f}],')

        self.assertTrue(ec.all_non_dominated(fvs))

    def test_run_econstraint_gurobi_mip(self):
        from gurobipy import Model as GurobiModel
        from gurobipy import GRB, quicksum

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
            zval = z.x
            solutions.append((xvals, yvals, zval))

        ec.run_econstraint(model=mdl,
                           objectives=objectives,
                           solution_extractor=extract_solution,
                           optimizer='gurobi')

        def f(i, sol):
            x, y, z = sol
            if i == 0:
                return sum(x[i] for i in parks)
            elif i == 1:
                return sum(distance[i, j] * y[i, j] for i in buildings for j in parks)
            else:
                return z

        fvs = [[f(i, sol) for i in range(3)] for sol in solutions]

        for fv in fvs:
            a, b, c = fv
            print(f'[{a:>5.1f}, {b:>7.1f}, {c:>5.1f}],')

        self.assertTrue(ec.all_weakly_non_dominated(fvs))

    def test_run_econstraint_gurobi_lp(self):
        from gurobipy import Model as GurobiModel
        from gurobipy import GRB, quicksum

        # define model
        mdl = GurobiModel()

        # define variables
        x = mdl.addVars(parks, vtype=GRB.CONTINUOUS, name='x')
        y = mdl.addVars([(i, j) for i in buildings for j in parks], vtype=GRB.CONTINUOUS, name='y')
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
            zval = z.x
            solutions.append((xvals, yvals, zval))

        ec.run_econstraint(model=mdl,

                           objectives=objectives,
                           solution_extractor=extract_solution,
                           optimizer='gurobi')

        def f(i, sol):
            x, y, z = sol
            if i == 0:
                return sum(x[i] for i in parks)
            elif i == 1:
                return sum(distance[i, j] * y[i, j] for i in buildings for j in parks)
            else:
                return z

        fvs = [[f(i, sol) for i in range(3)] for sol in solutions]

        for fv in fvs:
            a, b, c = fv
            print(f'[{a:>5.1f}, {b:>7.1f}, {c:>5.1f}],')

        self.assertTrue(ec.all_non_dominated(fvs))


if __name__ == '__main__':
    unittest.main()
